"""Instructor-only LMS API views."""

from decimal import Decimal

from django.db.models import Sum, Count
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.templatetags.static import static

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Course, Section, Lesson, Enrollment, Coupon,
    OrderItem, CourseReview, Question, Notification
)
from .permissions import IsInstructor
from api.serializer import (
    InstructorCourseWriteSerializer,
    InstructorCourseDetailSerializer, CouponSerializer,
    CourseReviewSerializer, QuestionSerializer, NotificationSerializer,
)


class InstructorCourseDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete an instructor's course."""
    permission_classes = [IsAuthenticated, IsInstructor]
    lookup_field = 'course_id'

    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user).prefetch_related(
            'sections__lessons', 'category'
        )

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return InstructorCourseWriteSerializer
        return InstructorCourseDetailSerializer


class InstructorSectionDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsInstructor]

    def delete(self, request, section_id):
        section = get_object_or_404(
            Section, section_id=section_id, course__instructor=request.user
        )
        course = section.course
        section.delete()
        course.total_sections = course.sections.count()
        course.total_lessons = sum(s.lessons.count() for s in course.sections.all())
        course.save(update_fields=['total_sections', 'total_lessons'])
        return Response({"message": "Section deleted"})


class InstructorLessonDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, IsInstructor]

    def delete(self, request, lesson_id):
        lesson = get_object_or_404(
            Lesson, lesson_id=lesson_id, section__course__instructor=request.user
        )
        course = lesson.section.course
        lesson.delete()
        course.total_lessons = sum(s.lessons.count() for s in course.sections.all())
        course.save(update_fields=['total_lessons'])
        return Response({"message": "Lesson deleted"})


class InstructorCouponDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsInstructor]
    serializer_class = CouponSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'coupon_id'

    def get_queryset(self):
        return Coupon.objects.filter(instructor=self.request.user)


class InstructorReviewsAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsInstructor]
    serializer_class = CourseReviewSerializer

    def get_queryset(self):
        return CourseReview.objects.filter(
            course__instructor=self.request.user
        ).select_related('student', 'student__profile', 'course').order_by('-created_at')


class InstructorStudentsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsInstructor]

    def get(self, request):
        enrollments = Enrollment.objects.filter(
            course__instructor=request.user
        ).select_related('student', 'student__profile').order_by('-enrolled_at')

        seen = set()
        students = []
        for enrollment in enrollments:
            if enrollment.student_id in seen:
                continue
            seen.add(enrollment.student_id)
            profile = getattr(enrollment.student, 'profile', None)
            image = None
            if profile and profile.image:
                image = request.build_absolute_uri(profile.image.url)
            students.append({
                "id": enrollment.student_id,
                "full_name": (profile.full_name if profile and profile.full_name else enrollment.student.full_name),
                "email": enrollment.student.email,
                "image": image,
                "country": profile.country if profile else None,
                "date": enrollment.enrolled_at,
            })
        return Response(students)


class InstructorOrdersAPIView(APIView):
    permission_classes = [IsAuthenticated, IsInstructor]

    def get(self, request):
        items = OrderItem.objects.filter(
            instructor=request.user,
            order__status='completed'
        ).select_related('course', 'order').order_by('-created_at')

        data = []
        for item in items:
            data.append({
                "id": item.id,
                "price": float(item.price),
                "date": item.created_at,
                "course": {
                    "title": item.course.title,
                    "course_id": item.course.course_id,
                    "thumbnail": request.build_absolute_uri(item.course.thumbnail.url) if item.course.thumbnail else None,
                },
                "order": {
                    "oid": item.order.order_id,
                    "order_id": item.order.order_id,
                    "status": item.order.status,
                },
            })
        return Response(data)


class InstructorQAAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsInstructor]
    serializer_class = QuestionSerializer

    def get_queryset(self):
        return Question.objects.filter(
            course__instructor=self.request.user
        ).select_related('student', 'student__profile', 'course').prefetch_related(
            'answers__user', 'answers__user__profile'
        ).order_by('-created_at')


class InstructorEarningsMonthlyAPIView(APIView):
    permission_classes = [IsAuthenticated, IsInstructor]

    def get(self, request):
        items = OrderItem.objects.filter(
            instructor=request.user,
            order__status='completed'
        )
        monthly = {}
        for item in items.select_related('order'):
            stamp = item.order.completed_at or item.created_at
            key = stamp.strftime('%B')
            monthly[key] = monthly.get(key, Decimal('0')) + item.price

        months = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        data = [{"month": month, "total": float(monthly.get(month, 0))} for month in months]
        return Response(data)


class InstructorBestCoursesAPIView(APIView):
    permission_classes = [IsAuthenticated, IsInstructor]

    def get(self, request):
        rows = OrderItem.objects.filter(
            instructor=request.user,
            order__status='completed'
        ).values(
            'course_id', 'course__title', 'course__thumbnail', 'course__course_id'
        ).annotate(
            sales=Count('id'),
            revenue=Sum('price')
        ).order_by('-revenue')[:10]

        data = []
        for row in rows:
            thumbnail = row.get('course__thumbnail')
            if thumbnail:
                image = request.build_absolute_uri(f"{settings.MEDIA_URL}{thumbnail}")
            else:
                image = request.build_absolute_uri(static('img/course-placeholder.svg'))
            data.append({
                "course_title": row['course__title'],
                "course_image": image,
                "sales": row['sales'],
                "revenue": float(row['revenue'] or 0),
            })
        return Response(data)


class InstructorNotificationsAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsInstructor]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')[:50]
