from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_password_reset_email(self, user_email, username, reset_link):
    """
    Send password reset email asynchronously
    """
    try:
        context = {
            "link": reset_link,
            "username": username
        }

        subject = "Password Reset Email"
        text_body = render_to_string("email/password_reset.txt", context)
        html_body = render_to_string("email/password_reset.html", context)

        msg = EmailMultiAlternatives(
            subject=subject,
            from_email=settings.FROM_EMAIL,
            to=[user_email],
            body=text_body
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send()

        logger.info(f"Password reset email sent to {user_email}")
        return True

    except Exception as exc:
        logger.error(f"Failed to send password reset email to {user_email}: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_enrollment_confirmation_email(self, user_email, username, course_title):
    """
    Send enrollment confirmation email asynchronously
    """
    try:
        context = {
            "username": username,
            "course_title": course_title
        }

        subject = f"Enrollment Confirmed: {course_title}"
        text_body = f"Hi {username},\n\nYou have been enrolled in {course_title}.\n\nHappy learning!"
        html_body = f"""
        <html>
        <body>
            <h2>Enrollment Confirmed!</h2>
            <p>Hi {username},</p>
            <p>You have been successfully enrolled in <strong>{course_title}</strong>.</p>
            <p>Happy learning!</p>
        </body>
        </html>
        """

        msg = EmailMultiAlternatives(
            subject=subject,
            from_email=settings.FROM_EMAIL,
            to=[user_email],
            body=text_body
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send()

        logger.info(f"Enrollment confirmation email sent to {user_email} for {course_title}")
        return True

    except Exception as exc:
        logger.error(f"Failed to send enrollment confirmation email: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_order_confirmation_email(self, user_email, username, order_id, total, courses):
    """
    Send order confirmation email asynchronously
    """
    try:
        subject = f"Order Confirmation #{order_id}"
        text_body = f"Hi {username},\n\nYour order #{order_id} has been confirmed.\n\nTotal: ${total}"

        course_list = '\n'.join([f"- {course}" for course in courses])
        html_body = f"""
        <html>
        <body>
            <h2>Order Confirmed!</h2>
            <p>Hi {username},</p>
            <p>Your order <strong>#{order_id}</strong> has been confirmed.</p>
            <h3>Courses:</h3>
            <ul>
                {''.join([f'<li>{course}</li>' for course in courses])}
            </ul>
            <p><strong>Total: ${total}</strong></p>
            <p>Thank you for your purchase!</p>
        </body>
        </html>
        """

        msg = EmailMultiAlternatives(
            subject=subject,
            from_email=settings.FROM_EMAIL,
            to=[user_email],
            body=text_body
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send()

        logger.info(f"Order confirmation email sent to {user_email} for order #{order_id}")
        return True

    except Exception as exc:
        logger.error(f"Failed to send order confirmation email: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task
def cleanup_expired_carts():
    """
    Periodic task to clean up abandoned carts older than 7 days
    """
    from django.utils import timezone
    from datetime import timedelta
    from core.models import Cart

    threshold = timezone.now() - timedelta(days=7)
    deleted_count, _ = Cart.objects.filter(
        updated_at__lt=threshold,
        user__isnull=True  # Only anonymous carts
    ).delete()

    logger.info(f"Cleaned up {deleted_count} abandoned carts")
    return deleted_count


@shared_task
def update_course_metrics(course_id):
    """
    Update course metrics (total students, average rating, etc.)
    """
    from core.models import Course, Enrollment, CourseReview
    from django.db.models import Avg, Count

    try:
        course = Course.objects.get(id=course_id)

        # Update total students
        course.total_students = Enrollment.objects.filter(
            course=course,
            status__in=['active', 'completed']
        ).count()

        # Update review metrics
        review_stats = CourseReview.objects.filter(
            course=course,
            is_approved=True
        ).aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id')
        )

        course.average_rating = review_stats['avg_rating'] or 0
        course.total_reviews = review_stats['total_reviews'] or 0

        # Update section/lesson counts
        course.total_sections = course.sections.count()
        course.total_lessons = sum(
            section.lessons.count() for section in course.sections.all()
        )
        course.total_duration = sum(
            lesson.duration for section in course.sections.all()
            for lesson in section.lessons.all()
        )

        course.save()

        logger.info(f"Updated metrics for course {course_id}")
        return True

    except Course.DoesNotExist:
        logger.error(f"Course {course_id} not found")
        return False
