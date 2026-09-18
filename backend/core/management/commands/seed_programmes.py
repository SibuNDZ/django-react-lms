"""
Seed the three DSN Research programme shells (courses, modules, lessons,
knowledge-check quizzes, practicals and capstones).

Idempotent: courses are matched by slug, sections by order and lessons by
(section, order), so re-running updates text without duplicating content.
Quiz questions are only written when a quiz is first created, so existing
attempts keep a consistent answer key; pass --reset-quizzes to replace them.

    python manage.py seed_programmes --instructor-email you@example.com --publish
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from core.models import (
    Category, Course, Section, Lesson,
    Quiz, QuizQuestion, QuizChoice, Assignment,
)
from core.seeds.programmes import CATEGORY, PROGRAMMES

User = get_user_model()

# Minutes, used for lesson durations and course totals
DURATIONS = {'overview': 30, 'concepts': 120, 'lab': 180, 'quiz': 20, 'practical': 300, 'capstone': 1200}


class Command(BaseCommand):
    help = "Create or update the three programme course shells with quizzes and practicals"

    def add_arguments(self, parser):
        parser.add_argument(
            '--instructor-email',
            help="Instructor who owns the courses (default: first instructor, else created)",
        )
        parser.add_argument('--publish', action='store_true', help="Set course status to published")
        parser.add_argument(
            '--reset-quizzes', action='store_true',
            help="Replace questions on existing quizzes (past attempts keep their own answer copies)",
        )
        parser.add_argument('--only', help="Seed a single programme by slug")

    def handle(self, *args, **options):
        instructor = self.resolve_instructor(options.get('instructor_email'))
        category, _ = Category.objects.get_or_create(
            name=CATEGORY['name'], defaults={'description': CATEGORY['description']}
        )

        programmes = PROGRAMMES
        if options.get('only'):
            programmes = [p for p in PROGRAMMES if p['slug'] == options['only']]
            if not programmes:
                raise CommandError(f"No programme with slug {options['only']}")

        for programme in programmes:
            with transaction.atomic():
                course, created = self.seed_course(programme, instructor, category, options['publish'])
                counts = self.seed_modules(course, programme, options['reset_quizzes'])
            self.stdout.write(self.style.SUCCESS(
                f"{'Created' if created else 'Updated'} {course.title}: "
                f"{counts['sections']} sections, {counts['lessons']} lessons, "
                f"{counts['quizzes']} quizzes, {counts['assignments']} assignments"
            ))

    # ------------------------------------------------------------------
    def resolve_instructor(self, email):
        if email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise CommandError(f"No user with email {email}")
            if not user.is_instructor():
                user.role = User.ROLE_INSTRUCTOR
                user.save(update_fields=['role'])
            return user
        user = User.objects.filter(role=User.ROLE_INSTRUCTOR).order_by('id').first()
        if user:
            return user
        user = User.objects.create_user(
            email='programmes@dsnresearch.com', username='dsn-programmes',
            full_name='DSN Research Programmes', role=User.ROLE_INSTRUCTOR,
        )
        user.set_unusable_password()
        user.save()
        self.stdout.write(self.style.WARNING(f"Created instructor account {user.email}"))
        return user

    def seed_course(self, programme, instructor, category, publish):
        defaults = {
            'title': programme['title'],
            'short_description': programme['short_description'],
            'description': programme['description'],
            'category': category,
            'instructor': instructor,
            'level': programme['level'],
            'tags': programme['tags'],
            'requirements': programme['requirements'],
            'what_you_learn': programme['what_you_learn'],
            'target_audience': programme['target_audience'],
            'price': 0,
            'is_free': True,
        }
        course, created = Course.objects.get_or_create(slug=programme['slug'], defaults=defaults)
        if not created:
            for field, value in defaults.items():
                if field != 'instructor':
                    setattr(course, field, value)
        if publish and course.status != 'published':
            course.status = 'published'
            course.published_at = course.published_at or timezone.now()
        course.save()
        return course, created

    def seed_modules(self, course, programme, reset_quizzes):
        counts = {'sections': 0, 'lessons': 0, 'quizzes': 0, 'assignments': 0}
        total_duration = 0

        for index, module in enumerate(programme['modules']):
            number = index + 1
            section = self.upsert_section(
                course, index, f"Module {number}: {module['title']}", module['weeks']
            )
            counts['sections'] += 1

            lessons = [
                ('overview', 'Module overview', 'text', module['overview']),
                ('concepts', 'Core concepts', 'text', module['concepts']),
                ('lab', 'Guided lab', 'text', module['lab']),
                ('quiz', f"Module {number} knowledge check", 'quiz', None),
                ('practical', f"Module {number} practical", 'assignment', module['practical']['instructions']),
            ]
            section_duration = 0
            for order, (kind, title, lesson_type, content) in enumerate(lessons):
                lesson = self.upsert_lesson(section, order, title, lesson_type, content, DURATIONS[kind])
                counts['lessons'] += 1
                section_duration += lesson.duration
                if kind == 'quiz':
                    self.upsert_quiz(lesson, f"{module['title']}: knowledge check", module['quiz'], reset_quizzes)
                    counts['quizzes'] += 1
                elif kind == 'practical':
                    self.upsert_assignment(lesson, module['practical']['title'], module['practical']['instructions'])
                    counts['assignments'] += 1

            section.total_lessons = len(lessons)
            section.total_duration = section_duration
            section.save(update_fields=['total_lessons', 'total_duration'])
            total_duration += section_duration

        # Capstone section
        capstone = programme['capstone']
        cap_index = len(programme['modules'])
        section = self.upsert_section(course, cap_index, 'Capstone project', 'Final weeks')
        counts['sections'] += 1
        brief = self.upsert_lesson(section, 0, 'Capstone brief', 'text', capstone['brief'], DURATIONS['overview'])
        project = self.upsert_lesson(section, 1, 'Capstone submission', 'assignment', capstone['instructions'], DURATIONS['capstone'])
        self.upsert_assignment(project, capstone['title'], capstone['instructions'], pass_mark=60, allow_resubmission=True)
        counts['lessons'] += 2
        counts['assignments'] += 1
        section.total_lessons = 2
        section.total_duration = brief.duration + project.duration
        section.save(update_fields=['total_lessons', 'total_duration'])
        total_duration += section.total_duration

        course.total_sections = counts['sections']
        course.total_lessons = counts['lessons']
        course.total_duration = total_duration
        course.save(update_fields=['total_sections', 'total_lessons', 'total_duration'])
        return counts

    # ------------------------------------------------------------------
    @staticmethod
    def upsert_section(course, order, title, description):
        section, created = Section.objects.get_or_create(
            course=course, order=order, defaults={'title': title, 'description': description}
        )
        if not created:
            section.title = title
            section.description = description
            section.save(update_fields=['title', 'description'])
        return section

    @staticmethod
    def upsert_lesson(section, order, title, lesson_type, content, duration):
        defaults = {
            'title': title, 'lesson_type': lesson_type, 'content': content,
            'description': (content or '')[:500] or None, 'duration': duration, 'is_published': True,
        }
        lesson = Lesson.objects.filter(section=section, order=order).first()
        if lesson:
            for field, value in defaults.items():
                setattr(lesson, field, value)
            lesson.save()
        else:
            lesson = Lesson.objects.create(section=section, order=order, **defaults)
        return lesson

    @staticmethod
    def upsert_quiz(lesson, title, questions, reset):
        quiz, created = Quiz.objects.get_or_create(
            lesson=lesson,
            defaults={'title': title, 'description': 'Answer all questions. Pass mark 70%.',
                      'pass_mark': 70, 'max_attempts': 3, 'time_limit_minutes': 20},
        )
        if not created:
            quiz.title = title
            quiz.save(update_fields=['title'])
        if created or reset:
            quiz.questions.all().delete()
            for q_order, question in enumerate(questions):
                obj = QuizQuestion.objects.create(
                    quiz=quiz, text=question['text'], question_type=question['question_type'],
                    points=1, order=q_order,
                )
                for c_order, (text, is_correct) in enumerate(question['choices']):
                    QuizChoice.objects.create(question=obj, text=text, is_correct=is_correct, order=c_order)
        return quiz

    @staticmethod
    def upsert_assignment(lesson, title, instructions, pass_mark=50, allow_resubmission=True):
        assignment, _ = Assignment.objects.update_or_create(
            lesson=lesson,
            defaults={'title': title, 'instructions': instructions, 'max_score': 100,
                      'pass_mark': pass_mark, 'allow_resubmission': allow_resubmission},
        )
        return assignment
