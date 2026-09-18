"""Tests for the seed_programmes management command."""

from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from .models import Course, Section, Lesson, Quiz, QuizAttempt, Assignment, Enrollment
from .seeds.programmes import PROGRAMMES
from .test_views import User


class SeedProgrammesTests(TestCase):

    def run_seed(self, *args):
        out = StringIO()
        call_command('seed_programmes', *args, stdout=out)
        return out.getvalue()

    def test_seeds_three_programmes_with_assessments(self):
        output = self.run_seed('--publish')
        self.assertEqual(Course.objects.count(), 3)
        self.assertIn('Created', output)

        for programme in PROGRAMMES:
            course = Course.objects.get(slug=programme['slug'])
            modules = len(programme['modules'])
            self.assertEqual(course.status, 'published')
            self.assertEqual(course.total_sections, modules + 1)
            self.assertEqual(course.total_lessons, modules * 5 + 2)
            self.assertEqual(Quiz.objects.filter(lesson__section__course=course).count(), modules)
            self.assertEqual(Assignment.objects.filter(lesson__section__course=course).count(), modules + 1)
            self.assertEqual(course.instructor.role, 'instructor')

        # Every quiz has questions with exactly the expected correctness shape
        for quiz in Quiz.objects.all():
            self.assertEqual(quiz.questions.count(), 3)
            for question in quiz.questions.all():
                correct = question.choices.filter(is_correct=True).count()
                if question.question_type == 'multiple':
                    self.assertGreater(correct, 1)
                else:
                    self.assertEqual(correct, 1)

    def test_rerun_is_idempotent_and_keeps_quiz_attempts(self):
        self.run_seed()
        quiz = Quiz.objects.first()
        student = User.objects.create_user(email='s@test.com', username='s', password='x')
        enrollment = Enrollment.objects.create(student=student, course=quiz.lesson.section.course)
        attempt = QuizAttempt.objects.create(quiz=quiz, enrollment=enrollment, status='submitted')
        question_ids = set(quiz.questions.values_list('question_id', flat=True))

        output = self.run_seed()
        self.assertIn('Updated', output)
        self.assertEqual(Course.objects.count(), 3)
        self.assertEqual(Section.objects.count(), sum(len(p['modules']) + 1 for p in PROGRAMMES))
        self.assertEqual(Lesson.objects.count(), sum(len(p['modules']) * 5 + 2 for p in PROGRAMMES))
        self.assertTrue(QuizAttempt.objects.filter(pk=attempt.pk).exists())
        self.assertEqual(set(quiz.questions.values_list('question_id', flat=True)), question_ids)

    def test_reset_quizzes_replaces_questions(self):
        self.run_seed()
        quiz = Quiz.objects.first()
        before = set(quiz.questions.values_list('question_id', flat=True))
        self.run_seed('--reset-quizzes')
        after = set(quiz.questions.values_list('question_id', flat=True))
        self.assertEqual(len(after), 3)
        self.assertFalse(before & after)

    def test_uses_named_instructor(self):
        owner = User.objects.create_user(email='owner@test.com', username='owner', password='x', role='student')
        self.run_seed('--instructor-email', 'owner@test.com', '--only', PROGRAMMES[0]['slug'])
        self.assertEqual(Course.objects.count(), 1)
        owner.refresh_from_db()
        self.assertEqual(Course.objects.get().instructor, owner)
        self.assertEqual(owner.role, 'instructor')
