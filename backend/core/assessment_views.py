"""
Assessment API: quizzes, quiz attempts, assignments and submissions.

Instructor endpoints author the assessments attached to a lesson and
grade submissions. Student endpoints take quizzes and hand in
assignments. Passing an assessment is what completes a quiz or
assignment lesson; see core.progress.
"""

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Lesson, Enrollment, Quiz, QuizQuestion, QuizChoice, QuizAttempt,
    Assignment, AssignmentSubmission,
)
from .permissions import IsInstructor
from .progress import complete_lesson
from .grading import grade_quiz_attempt, expire_quiz_attempt
from .views import StandardResultsSetPagination
from api.serializer import (
    QuizWriteSerializer, QuizInstructorSerializer, QuizStudentSerializer,
    QuizAttemptSerializer, QuizSubmitSerializer,
    AssignmentWriteSerializer, AssignmentSerializer,
    AssignmentSubmissionSerializer, AssignmentSubmissionCreateSerializer,
    GradeSubmissionSerializer,
)


# ============== Shared lookups ==============

class InstructorLessonMixin:
    """Resolve a lesson that belongs to one of the instructor's own courses."""

    def get_lesson(self):
        return get_object_or_404(
            Lesson,
            lesson_id=self.kwargs['lesson_id'],
            section__course__instructor=self.request.user,
        )


class StudentLessonMixin:
    """Resolve the student's enrollment and a published lesson in that course."""

    def get_enrollment(self):
        return get_object_or_404(
            Enrollment,
            enrollment_id=self.kwargs['enrollment_id'],
            student=self.request.user,
        )

    def get_lesson(self, enrollment):
        return get_object_or_404(
            Lesson,
            lesson_id=self.kwargs['lesson_id'],
            section__course=enrollment.course,
            is_published=True,
        )


def quiz_status_payload(quiz, enrollment, request):
    """The student's standing on a quiz: attempts so far and what is left."""
    attempts = list(quiz.attempts.filter(enrollment=enrollment))
    submitted = [a for a in attempts if a.status == 'submitted']
    return {
        'quiz': QuizStudentSerializer(quiz, context={'request': request}).data,
        'attempts': QuizAttemptSerializer(attempts, many=True).data,
        'attempts_used': len(attempts),
        'attempts_remaining': (
            None if quiz.max_attempts == 0 else max(0, quiz.max_attempts - len(attempts))
        ),
        'best_percentage': max((a.percentage for a in submitted), default=None),
        'passed': any(a.outcome == 'competent' for a in submitted),
    }


# ============== Instructor: quizzes ==============

class InstructorQuizAPIView(InstructorLessonMixin, APIView):
    """
    GET the quiz attached to a lesson, or PUT to create/replace it.

    PUT replaces the whole question set. Past attempts keep their own
    copy of the selected and correct answers, so re-authoring a quiz does
    not rewrite history, but attempt answer keys will no longer match the
    live questions.
    """
    permission_classes = [IsAuthenticated, IsInstructor]

    def get(self, request, lesson_id):
        lesson = self.get_lesson()
        quiz = get_object_or_404(Quiz, lesson=lesson)
        return Response(QuizInstructorSerializer(quiz).data)

    @transaction.atomic
    def put(self, request, lesson_id):
        lesson = self.get_lesson()
        serializer = QuizWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = dict(serializer.validated_data)
        questions = data.pop('questions')
        quiz, created = Quiz.objects.update_or_create(lesson=lesson, defaults=data)

        quiz.questions.all().delete()
        for q_index, question_data in enumerate(questions):
            choices = question_data.pop('choices')
            order = question_data.pop('order', q_index)
            question = QuizQuestion.objects.create(quiz=quiz, order=order, **question_data)
            for c_index, choice_data in enumerate(choices):
                c_order = choice_data.pop('order', c_index)
                QuizChoice.objects.create(question=question, order=c_order, **choice_data)

        if lesson.lesson_type != 'quiz':
            lesson.lesson_type = 'quiz'
            lesson.save(update_fields=['lesson_type'])

        return Response(
            QuizInstructorSerializer(quiz).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class InstructorQuizAttemptListAPIView(InstructorLessonMixin, generics.ListAPIView):
    """All students' attempts on a lesson's quiz, newest first."""
    permission_classes = [IsAuthenticated, IsInstructor]
    serializer_class = QuizAttemptSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        lesson = self.get_lesson()
        return QuizAttempt.objects.filter(quiz__lesson=lesson).select_related(
            'enrollment__student'
        )


# ============== Instructor: assignments ==============

class InstructorAssignmentAPIView(InstructorLessonMixin, APIView):
    """GET the assignment attached to a lesson, or PUT to create/update it."""
    permission_classes = [IsAuthenticated, IsInstructor]

    def get(self, request, lesson_id):
        lesson = self.get_lesson()
        assignment = get_object_or_404(Assignment, lesson=lesson)
        return Response(AssignmentSerializer(assignment).data)

    def put(self, request, lesson_id):
        lesson = self.get_lesson()
        serializer = AssignmentWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        assignment, created = Assignment.objects.update_or_create(
            lesson=lesson, defaults=serializer.validated_data
        )
        if lesson.lesson_type != 'assignment':
            lesson.lesson_type = 'assignment'
            lesson.save(update_fields=['lesson_type'])

        return Response(
            AssignmentSerializer(assignment).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class InstructorAssignmentSubmissionListAPIView(InstructorLessonMixin, generics.ListAPIView):
    """All submissions on a lesson's assignment, newest first."""
    permission_classes = [IsAuthenticated, IsInstructor]
    serializer_class = AssignmentSubmissionSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        lesson = self.get_lesson()
        return AssignmentSubmission.objects.filter(
            assignment__lesson=lesson
        ).select_related('assignment', 'enrollment__student', 'graded_by')


class InstructorGradeSubmissionAPIView(APIView):
    """Record a score and feedback; a passing score completes the lesson."""
    permission_classes = [IsAuthenticated, IsInstructor]

    def post(self, request, submission_id):
        submission = get_object_or_404(
            AssignmentSubmission.objects.select_related('assignment__lesson', 'enrollment'),
            submission_id=submission_id,
            assignment__lesson__section__course__instructor=request.user,
        )
        serializer = GradeSubmissionSerializer(
            data=request.data, context={'assignment': submission.assignment}
        )
        serializer.is_valid(raise_exception=True)

        assignment = submission.assignment
        submission.score = serializer.validated_data['score']
        submission.feedback = serializer.validated_data.get('feedback', '')
        submission.status = 'graded'
        submission.graded_by = request.user
        submission.graded_at = timezone.now()
        percentage = (submission.score / assignment.max_score * 100) if assignment.max_score else 0
        submission.outcome = 'competent' if percentage >= assignment.pass_mark else 'not_yet_competent'
        submission.save()

        if submission.outcome == 'competent':
            complete_lesson(submission.enrollment, assignment.lesson)

        return Response(
            AssignmentSubmissionSerializer(submission, context={'request': request}).data
        )


# ============== Student: quizzes ==============

class StudentQuizAPIView(StudentLessonMixin, APIView):
    """The quiz for a lesson (without answer keys) and the student's attempts."""
    permission_classes = [IsAuthenticated]

    def get(self, request, enrollment_id, lesson_id):
        enrollment = self.get_enrollment()
        lesson = self.get_lesson(enrollment)
        quiz = get_object_or_404(Quiz, lesson=lesson, is_published=True)
        return Response(quiz_status_payload(quiz, enrollment, request))


class StudentQuizAttemptStartAPIView(StudentLessonMixin, APIView):
    """Open an attempt. Returns the open attempt if one is still running."""
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, enrollment_id, lesson_id):
        enrollment = self.get_enrollment()
        lesson = self.get_lesson(enrollment)
        quiz = get_object_or_404(Quiz, lesson=lesson, is_published=True)

        attempts = quiz.attempts.filter(enrollment=enrollment)
        open_attempt = attempts.filter(status='in_progress').first()
        if open_attempt:
            if open_attempt.is_expired:
                expire_quiz_attempt(open_attempt)
            else:
                return Response(QuizAttemptSerializer(open_attempt).data)

        used = attempts.count()
        if quiz.max_attempts and used >= quiz.max_attempts:
            return Response(
                {"message": "No attempts remaining for this quiz"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        attempt = QuizAttempt.objects.create(
            quiz=quiz, enrollment=enrollment, attempt_number=used + 1
        )
        return Response(QuizAttemptSerializer(attempt).data, status=status.HTTP_201_CREATED)


class StudentQuizAttemptSubmitAPIView(StudentLessonMixin, APIView):
    """Submit answers for an open attempt. Grading happens here, server-side."""
    permission_classes = [IsAuthenticated]

    def post(self, request, enrollment_id, lesson_id, attempt_id):
        enrollment = self.get_enrollment()
        lesson = self.get_lesson(enrollment)
        quiz = get_object_or_404(Quiz, lesson=lesson)
        attempt = get_object_or_404(
            QuizAttempt, attempt_id=attempt_id, quiz=quiz, enrollment=enrollment
        )

        if attempt.status != 'in_progress':
            return Response(
                {"message": "This attempt has already been submitted"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if attempt.is_expired:
            expire_quiz_attempt(attempt)
            return Response(
                {
                    "message": "Time limit exceeded; the attempt has been closed",
                    "attempt": QuizAttemptSerializer(attempt).data,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = QuizSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            grade_quiz_attempt(attempt, serializer.validated_data['answers'])
        except ValueError as exc:
            return Response({"message": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        if attempt.outcome == 'competent':
            complete_lesson(enrollment, lesson)

        payload = quiz_status_payload(quiz, enrollment, request)
        payload['attempt'] = QuizAttemptSerializer(attempt).data
        return Response(payload)


# ============== Student: assignments ==============

class StudentAssignmentAPIView(StudentLessonMixin, APIView):
    """The assignment for a lesson and the student's submissions on it."""
    permission_classes = [IsAuthenticated]

    def get(self, request, enrollment_id, lesson_id):
        enrollment = self.get_enrollment()
        lesson = self.get_lesson(enrollment)
        assignment = get_object_or_404(Assignment, lesson=lesson, is_published=True)
        submissions = list(assignment.submissions.filter(enrollment=enrollment))
        passed = any(s.outcome == 'competent' for s in submissions)
        return Response({
            'assignment': AssignmentSerializer(assignment).data,
            'submissions': AssignmentSubmissionSerializer(
                submissions, many=True, context={'request': request}
            ).data,
            'can_submit': not passed and (not submissions or assignment.allow_resubmission),
            'passed': passed,
        })


class StudentAssignmentSubmitAPIView(StudentLessonMixin, APIView):
    """Hand in a file, text, a link, or any combination."""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request, enrollment_id, lesson_id):
        enrollment = self.get_enrollment()
        lesson = self.get_lesson(enrollment)
        assignment = get_object_or_404(Assignment, lesson=lesson, is_published=True)

        existing = assignment.submissions.filter(enrollment=enrollment)
        if existing.filter(outcome='competent').exists():
            return Response(
                {"message": "This assignment has already been marked competent"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if existing.exists() and not assignment.allow_resubmission:
            return Response(
                {"message": "This assignment does not allow resubmission"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AssignmentSubmissionCreateSerializer(
            data=request.data, context={'assignment': assignment}
        )
        serializer.is_valid(raise_exception=True)
        submission = serializer.save(
            assignment=assignment,
            enrollment=enrollment,
            attempt_number=existing.count() + 1,
        )
        return Response(
            AssignmentSubmissionSerializer(submission, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )
