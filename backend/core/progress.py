"""
Enrollment progress bookkeeping.

Shared by the manual lesson-progress endpoint and by assessment outcomes
(quiz attempts and graded assignment submissions), so that "lesson
complete" means the same thing whichever path recorded it.
"""

from django.utils import timezone

from .models import LessonProgress

# Lessons whose completion is decided by an assessment outcome, never by
# the student ticking a box.
ASSESSED_LESSON_TYPES = ('quiz', 'assignment')


def complete_lesson(enrollment, lesson):
    """Mark a lesson complete for an enrollment (idempotent) and refresh totals."""
    progress, _ = LessonProgress.objects.get_or_create(
        enrollment=enrollment, lesson=lesson
    )
    if not progress.is_completed:
        progress.is_completed = True
        progress.completed_at = timezone.now()
        progress.save()
        enrollment.lessons_completed += 1
    refresh_enrollment_progress(enrollment)
    return progress


def refresh_enrollment_progress(enrollment):
    """Recompute the percentage and completion status from lessons_completed."""
    total_lessons = enrollment.course.total_lessons
    if total_lessons > 0:
        enrollment.progress_percentage = min(
            100, int((enrollment.lessons_completed / total_lessons) * 100)
        )
        if enrollment.progress_percentage >= 100 and enrollment.status != 'completed':
            enrollment.status = 'completed'
            enrollment.completed_at = timezone.now()
    enrollment.last_accessed = timezone.now()
    enrollment.save()
