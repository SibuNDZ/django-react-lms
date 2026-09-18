"""
API tests for quizzes, quiz attempts, assignments and submissions.

Run with: python manage.py test core.test_assessments
"""

import shutil
import tempfile
from datetime import timedelta
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.utils import timezone
from rest_framework import status

from .models import (
    Lesson, Enrollment, LessonProgress,
    Quiz, QuizQuestion, QuizChoice, QuizAttempt,
    Assignment, AssignmentSubmission,
)
from .test_views import BaseAPITestCase, User


QUIZ_PAYLOAD = {
    "title": "Python basics check",
    "pass_mark": 50,
    "max_attempts": 0,
    "questions": [
        {
            "text": "Which keyword defines a function?",
            "question_type": "single",
            "points": 1,
            "choices": [
                {"text": "def", "is_correct": True},
                {"text": "func", "is_correct": False},
                {"text": "function", "is_correct": False},
            ],
        },
        {
            "text": "Which of these are sequence types?",
            "question_type": "multiple",
            "points": 2,
            "choices": [
                {"text": "list", "is_correct": True},
                {"text": "tuple", "is_correct": True},
                {"text": "dict", "is_correct": False},
            ],
        },
    ],
}


TEMP_MEDIA_ROOT = tempfile.mkdtemp(prefix='lms-test-media-')


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class AssessmentTestCase(BaseAPITestCase):
    """Adds a quiz lesson, an assignment lesson and an enrolled student.

    Uploads go to a throwaway MEDIA_ROOT so test files never land in the repo.
    """

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        super().setUp()
        self.quiz_lesson = Lesson.objects.create(
            section=self.section, title='Check your understanding', lesson_type='quiz', order=1
        )
        self.assignment_lesson = Lesson.objects.create(
            section=self.section, title='Build a CLI', lesson_type='assignment', order=2
        )
        self.course.total_lessons = 3
        self.course.save()
        self.enrollment = Enrollment.objects.create(student=self.student, course=self.course)

        self.other_instructor = User.objects.create_user(
            email='other-instructor@test.com', username='otherinstructor',
            password='testpass123', role='instructor',
        )

    # helpers
    def instructor_quiz_url(self, lesson=None):
        lesson = lesson or self.quiz_lesson
        return f'/api/v1/instructor/lessons/{lesson.lesson_id}/quiz/'

    def student_quiz_url(self, suffix=''):
        return (
            f'/api/v1/student/enrollments/{self.enrollment.enrollment_id}'
            f'/lessons/{self.quiz_lesson.lesson_id}/quiz/{suffix}'
        )

    def student_assignment_url(self, suffix=''):
        return (
            f'/api/v1/student/enrollments/{self.enrollment.enrollment_id}'
            f'/lessons/{self.assignment_lesson.lesson_id}/assignment/{suffix}'
        )

    def create_quiz(self, **overrides):
        self.authenticate_as_instructor()
        payload = {**QUIZ_PAYLOAD, **overrides}
        response = self.client.put(self.instructor_quiz_url(), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.client.force_authenticate(user=None)
        return Quiz.objects.get(lesson=self.quiz_lesson)

    def correct_answers(self, quiz):
        answers = {}
        for question in quiz.questions.all():
            answers[question.question_id] = [
                c.choice_id for c in question.choices.filter(is_correct=True)
            ]
        return answers

    def start_attempt(self):
        response = self.client.post(self.student_quiz_url('attempts/'))
        self.assertIn(response.status_code, (status.HTTP_200_OK, status.HTTP_201_CREATED), response.data)
        return response.data['attempt_id']

    def submit(self, attempt_id, answers):
        return self.client.post(
            self.student_quiz_url(f'attempts/{attempt_id}/submit/'),
            {'answers': answers}, format='json'
        )


class InstructorQuizAuthoringTests(AssessmentTestCase):

    def test_put_creates_quiz_with_questions_and_sets_lesson_type(self):
        self.quiz_lesson.lesson_type = 'video'
        self.quiz_lesson.save()
        quiz = self.create_quiz()
        self.assertEqual(quiz.questions.count(), 2)
        self.assertEqual(quiz.total_points, 3)
        self.quiz_lesson.refresh_from_db()
        self.assertEqual(self.quiz_lesson.lesson_type, 'quiz')

    def test_put_again_replaces_questions(self):
        self.create_quiz()
        self.authenticate_as_instructor()
        payload = {**QUIZ_PAYLOAD, "questions": QUIZ_PAYLOAD["questions"][:1], "pass_mark": 80}
        response = self.client.put(self.instructor_quiz_url(), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        quiz = Quiz.objects.get(lesson=self.quiz_lesson)
        self.assertEqual(quiz.questions.count(), 1)
        self.assertEqual(quiz.pass_mark, 80)
        self.assertEqual(Quiz.objects.count(), 1)

    def test_get_includes_answer_key_for_instructor(self):
        self.create_quiz()
        self.authenticate_as_instructor()
        response = self.client.get(self.instructor_quiz_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('is_correct', response.data['questions'][0]['choices'][0])

    def test_single_answer_question_with_two_correct_choices_is_rejected(self):
        self.authenticate_as_instructor()
        bad = {
            **QUIZ_PAYLOAD,
            "questions": [{
                "text": "Bad", "question_type": "single",
                "choices": [{"text": "a", "is_correct": True}, {"text": "b", "is_correct": True}],
            }],
        }
        response = self.client.put(self.instructor_quiz_url(), bad, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Quiz.objects.exists())

    def test_quiz_needs_a_question(self):
        self.authenticate_as_instructor()
        response = self.client.put(self.instructor_quiz_url(), {**QUIZ_PAYLOAD, "questions": []}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_other_instructor_cannot_author_on_this_course(self):
        self.client.force_authenticate(user=self.other_instructor)
        response = self.client.put(self.instructor_quiz_url(), QUIZ_PAYLOAD, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_cannot_author(self):
        self.authenticate_as_student()
        response = self.client.put(self.instructor_quiz_url(), QUIZ_PAYLOAD, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class StudentQuizTests(AssessmentTestCase):

    def test_student_sees_quiz_without_answer_key(self):
        self.create_quiz()
        self.authenticate_as_student()
        response = self.client.get(self.student_quiz_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        question = response.data['quiz']['questions'][0]
        self.assertNotIn('is_correct', question['choices'][0])
        self.assertNotIn('explanation', question)
        self.assertEqual(response.data['attempts_used'], 0)
        self.assertIsNone(response.data['attempts_remaining'])
        self.assertFalse(response.data['passed'])

    def test_unenrolled_student_gets_404(self):
        self.create_quiz()
        outsider = User.objects.create_user(email='out@test.com', username='out', password='x')
        self.client.force_authenticate(user=outsider)
        self.assertEqual(self.client.get(self.student_quiz_url()).status_code, status.HTTP_404_NOT_FOUND)

    def test_unpublished_quiz_is_hidden(self):
        self.create_quiz(is_published=False)
        self.authenticate_as_student()
        self.assertEqual(self.client.get(self.student_quiz_url()).status_code, status.HTTP_404_NOT_FOUND)

    def test_passing_attempt_is_graded_and_completes_lesson(self):
        quiz = self.create_quiz()
        self.authenticate_as_student()
        attempt_id = self.start_attempt()

        response = self.submit(attempt_id, self.correct_answers(quiz))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        attempt = response.data['attempt']
        self.assertEqual(attempt['status'], 'submitted')
        self.assertEqual(attempt['outcome'], 'competent')
        self.assertEqual(Decimal(attempt['percentage']), Decimal('100.00'))
        self.assertEqual(Decimal(attempt['score']), Decimal('3.00'))
        self.assertTrue(response.data['passed'])

        progress = LessonProgress.objects.get(enrollment=self.enrollment, lesson=self.quiz_lesson)
        self.assertTrue(progress.is_completed)
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.lessons_completed, 1)
        self.assertEqual(self.enrollment.progress_percentage, 33)

    def test_partial_credit_below_pass_mark_is_not_yet_competent(self):
        quiz = self.create_quiz(pass_mark=70)
        self.authenticate_as_student()
        attempt_id = self.start_attempt()

        answers = self.correct_answers(quiz)
        multiple = quiz.questions.get(question_type='multiple')
        answers[multiple.question_id] = answers[multiple.question_id][:1]  # one of two
        response = self.submit(attempt_id, answers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['attempt']['outcome'], 'not_yet_competent')
        self.assertEqual(Decimal(response.data['attempt']['percentage']), Decimal('33.33'))
        self.assertFalse(
            LessonProgress.objects.filter(
                enrollment=self.enrollment, lesson=self.quiz_lesson, is_completed=True
            ).exists()
        )

    def test_unanswered_questions_score_zero(self):
        self.create_quiz()
        self.authenticate_as_student()
        attempt_id = self.start_attempt()
        response = self.submit(attempt_id, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(response.data['attempt']['percentage']), Decimal('0.00'))

    def test_max_attempts_is_enforced(self):
        quiz = self.create_quiz(max_attempts=1)
        self.authenticate_as_student()
        attempt_id = self.start_attempt()
        self.submit(attempt_id, {})
        response = self.client.post(self.student_quiz_url('attempts/'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(quiz.attempts.count(), 1)

    def test_starting_again_returns_the_open_attempt(self):
        self.create_quiz()
        self.authenticate_as_student()
        first = self.start_attempt()
        response = self.client.post(self.student_quiz_url('attempts/'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['attempt_id'], first)

    def test_submitted_attempt_cannot_be_resubmitted(self):
        self.create_quiz()
        self.authenticate_as_student()
        attempt_id = self.start_attempt()
        self.submit(attempt_id, {})
        self.assertEqual(self.submit(attempt_id, {}).status_code, status.HTTP_400_BAD_REQUEST)

    def test_unknown_choice_id_is_rejected(self):
        quiz = self.create_quiz()
        self.authenticate_as_student()
        attempt_id = self.start_attempt()
        question = quiz.questions.first()
        response = self.submit(attempt_id, {question.question_id: ['NOPE']})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        attempt = QuizAttempt.objects.get(attempt_id=attempt_id)
        self.assertEqual(attempt.status, 'in_progress')

    def test_expired_attempt_is_closed_on_submit(self):
        quiz = self.create_quiz(time_limit_minutes=5)
        self.authenticate_as_student()
        attempt_id = self.start_attempt()
        QuizAttempt.objects.filter(attempt_id=attempt_id).update(
            started_at=timezone.now() - timedelta(minutes=10)
        )
        response = self.submit(attempt_id, self.correct_answers(quiz))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        attempt = QuizAttempt.objects.get(attempt_id=attempt_id)
        self.assertEqual(attempt.status, 'submitted')
        self.assertEqual(attempt.outcome, 'not_yet_competent')

    def test_manual_completion_of_quiz_lesson_is_refused(self):
        self.create_quiz()
        self.authenticate_as_student()
        response = self.client.post(
            f'/api/v1/student/progress/{self.enrollment.enrollment_id}/',
            {'lesson_id': self.quiz_lesson.lesson_id, 'is_completed': True},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(LessonProgress.objects.filter(lesson=self.quiz_lesson).exists())

    def test_video_lesson_can_still_be_completed_manually(self):
        self.authenticate_as_student()
        response = self.client.post(
            f'/api/v1/student/progress/{self.enrollment.enrollment_id}/',
            {'lesson_id': self.lesson.lesson_id, 'is_completed': True, 'time_spent': 30},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['lessons_completed'], 1)
        self.assertEqual(response.data['progress_percentage'], 33)

    def test_instructor_can_list_attempts(self):
        quiz = self.create_quiz()
        self.authenticate_as_student()
        self.submit(self.start_attempt(), self.correct_answers(quiz))
        self.authenticate_as_instructor()
        response = self.client.get(self.instructor_quiz_url() + 'attempts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['student']['email'], 'student@test.com')


ASSIGNMENT_PAYLOAD = {
    "title": "Build a command-line todo app",
    "instructions": "Submit a zip of your project and a short write-up.",
    "max_score": 100,
    "pass_mark": 50,
    "allow_resubmission": True,
}


class AssignmentTests(AssessmentTestCase):

    def instructor_assignment_url(self, suffix=''):
        return f'/api/v1/instructor/lessons/{self.assignment_lesson.lesson_id}/assignment/{suffix}'

    def create_assignment(self, **overrides):
        self.authenticate_as_instructor()
        response = self.client.put(
            self.instructor_assignment_url(), {**ASSIGNMENT_PAYLOAD, **overrides}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.client.force_authenticate(user=None)
        return Assignment.objects.get(lesson=self.assignment_lesson)

    def test_instructor_creates_and_updates_assignment(self):
        assignment = self.create_assignment()
        self.assertEqual(assignment.max_score, 100)
        self.authenticate_as_instructor()
        response = self.client.put(
            self.instructor_assignment_url(), {**ASSIGNMENT_PAYLOAD, "pass_mark": 60}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assignment.refresh_from_db()
        self.assertEqual(assignment.pass_mark, 60)
        self.assertEqual(Assignment.objects.count(), 1)

    def test_student_sees_assignment_and_can_submit_text(self):
        self.create_assignment()
        self.authenticate_as_student()
        response = self.client.get(self.student_assignment_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['can_submit'])

        response = self.client.post(
            self.student_assignment_url('submissions/'),
            {'text_answer': 'Here is my write-up', 'link': 'https://github.com/example/todo'},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['status'], 'submitted')
        self.assertEqual(response.data['outcome'], 'pending')
        self.assertEqual(response.data['attempt_number'], 1)

    def test_file_upload_respects_allowed_types(self):
        self.create_assignment(allowed_file_types='zip,pdf')
        self.authenticate_as_student()
        bad = SimpleUploadedFile('malware.exe', b'MZ', content_type='application/octet-stream')
        response = self.client.post(self.student_assignment_url('submissions/'), {'file': bad}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        good = SimpleUploadedFile('project.zip', b'PK\x03\x04', content_type='application/zip')
        response = self.client.post(self.student_assignment_url('submissions/'), {'file': good}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertTrue(response.data['file_name'].startswith('project'))
        self.assertTrue(response.data['file_name'].endswith('.zip'))
        self.assertTrue(response.data['file'])

    def test_empty_submission_is_rejected(self):
        self.create_assignment()
        self.authenticate_as_student()
        response = self.client.post(self.student_assignment_url('submissions/'), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_resubmission_blocked_when_disabled(self):
        self.create_assignment(allow_resubmission=False)
        self.authenticate_as_student()
        self.client.post(self.student_assignment_url('submissions/'), {'text_answer': 'v1'})
        response = self.client.post(self.student_assignment_url('submissions/'), {'text_answer': 'v2'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(AssignmentSubmission.objects.count(), 1)

    def test_grading_competent_completes_lesson(self):
        assignment = self.create_assignment()
        self.authenticate_as_student()
        response = self.client.post(self.student_assignment_url('submissions/'), {'text_answer': 'done'})
        submission_id = response.data['submission_id']

        self.authenticate_as_instructor()
        response = self.client.post(
            f'/api/v1/instructor/submissions/{submission_id}/grade/',
            {'score': '72.5', 'feedback': 'Good structure, add tests'}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data['status'], 'graded')
        self.assertEqual(response.data['outcome'], 'competent')
        self.assertEqual(response.data['graded_by']['id'], self.instructor.id)

        progress = LessonProgress.objects.get(enrollment=self.enrollment, lesson=self.assignment_lesson)
        self.assertTrue(progress.is_completed)

        # A competent submission closes the assignment for that student
        self.authenticate_as_student()
        response = self.client.get(self.student_assignment_url())
        self.assertTrue(response.data['passed'])
        self.assertFalse(response.data['can_submit'])
        self.assertEqual(
            self.client.post(self.student_assignment_url('submissions/'), {'text_answer': 'again'}).status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(assignment.submissions.count(), 1)

    def test_grading_below_pass_mark_is_not_yet_competent(self):
        self.create_assignment(pass_mark=60)
        self.authenticate_as_student()
        submission_id = self.client.post(
            self.student_assignment_url('submissions/'), {'text_answer': 'done'}
        ).data['submission_id']
        self.authenticate_as_instructor()
        response = self.client.post(
            f'/api/v1/instructor/submissions/{submission_id}/grade/', {'score': 40}, format='json'
        )
        self.assertEqual(response.data['outcome'], 'not_yet_competent')
        self.assertFalse(LessonProgress.objects.filter(lesson=self.assignment_lesson, is_completed=True).exists())

    def test_score_above_max_is_rejected(self):
        self.create_assignment(max_score=10)
        self.authenticate_as_student()
        submission_id = self.client.post(
            self.student_assignment_url('submissions/'), {'text_answer': 'done'}
        ).data['submission_id']
        self.authenticate_as_instructor()
        response = self.client.post(
            f'/api/v1/instructor/submissions/{submission_id}/grade/', {'score': 11}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_other_instructor_cannot_grade_or_list(self):
        self.create_assignment()
        self.authenticate_as_student()
        submission_id = self.client.post(
            self.student_assignment_url('submissions/'), {'text_answer': 'done'}
        ).data['submission_id']
        self.client.force_authenticate(user=self.other_instructor)
        self.assertEqual(
            self.client.post(f'/api/v1/instructor/submissions/{submission_id}/grade/', {'score': 5}, format='json').status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertEqual(
            self.client.get(self.instructor_assignment_url('submissions/')).status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_instructor_lists_submissions(self):
        self.create_assignment()
        self.authenticate_as_student()
        self.client.post(self.student_assignment_url('submissions/'), {'text_answer': 'done'})
        self.authenticate_as_instructor()
        response = self.client.get(self.instructor_assignment_url('submissions/'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['student']['email'], 'student@test.com')

    def test_manual_completion_of_assignment_lesson_is_refused(self):
        self.create_assignment()
        self.authenticate_as_student()
        response = self.client.post(
            f'/api/v1/student/progress/{self.enrollment.enrollment_id}/',
            {'lesson_id': self.assignment_lesson.lesson_id, 'is_completed': True},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
