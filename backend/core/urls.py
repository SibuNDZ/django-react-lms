"""
Core LMS URL Configuration

This module defines all URL routes for:
- Course browsing and searching
- Shopping cart management
- Order and checkout processing
- Student enrollment and progress tracking
- Reviews and Q&A
- Wishlist management
- Instructor features
"""

from django.urls import path
from . import views

urlpatterns = [
    # ============== Categories ==============
    path('categories/', views.CategoryListAPIView.as_view(), name='category-list'),
    path('categories/<slug:slug>/', views.CategoryDetailAPIView.as_view(), name='category-detail'),

    # ============== Courses ==============
    path('courses/', views.CourseListAPIView.as_view(), name='course-list'),
    path('courses/featured/', views.FeaturedCourseListAPIView.as_view(), name='course-featured'),
    path('courses/search/', views.CourseSearchAPIView.as_view(), name='course-search'),
    path('courses/<slug:slug>/', views.CourseDetailAPIView.as_view(), name='course-detail'),
    path('courses/<slug:course_slug>/reviews/', views.CourseReviewListAPIView.as_view(), name='course-reviews'),
    path('courses/<slug:course_slug>/reviews/create/', views.CourseReviewCreateAPIView.as_view(), name='course-review-create'),
    path('courses/<slug:course_slug>/qa/', views.CourseQAListAPIView.as_view(), name='course-qa'),
    path('courses/<slug:course_slug>/qa/create/', views.QuestionCreateAPIView.as_view(), name='question-create'),
    path('courses/<slug:course_slug>/lessons/<str:lesson_id>/', views.LessonDetailAPIView.as_view(), name='lesson-detail'),
    # Frontend compatibility alias for course listing
    path('course/course-list/', views.CourseListAPIView.as_view(), name='course-list-compat'),

    # Instructor's public courses
    path('instructors/<int:instructor_id>/courses/', views.InstructorPublicCoursesAPIView.as_view(), name='instructor-courses'),

    # ============== Cart ==============
    path('cart/', views.CartAPIView.as_view(), name='cart'),
    path('cart/<str:cart_id>/', views.CartAPIView.as_view(), name='cart-detail'),
    path('cart/add/', views.CartItemAddAPIView.as_view(), name='cart-add'),
    path('cart/<str:cart_id>/remove/<str:course_id>/', views.CartItemRemoveAPIView.as_view(), name='cart-remove'),
    path('cart/<str:cart_id>/clear/', views.CartClearAPIView.as_view(), name='cart-clear'),
    path('cart/stats/', views.CartStatsAPIView.as_view(), name='cart-stats'),
    path('cart/stats/<str:cart_id>/', views.CartStatsAPIView.as_view(), name='cart-stats-detail'),
    # Frontend compatibility aliases
    path('course/cart-list/<str:cart_id>/', views.CartAPIView.as_view(), name='cart-list-compat'),

    # ============== Orders ==============
    path('order/create/', views.OrderCreateAPIView.as_view(), name='order-create'),
    path('order/create-order/', views.OrderCreateAPIView.as_view(), name='order-create-compat'),
    path('order/list/', views.OrderListAPIView.as_view(), name='order-list'),
    path('order/checkout/<str:order_oid>/', views.OrderDetailAPIView.as_view(), name='order-detail'),
    path('order/coupon/', views.CouponApplyAPIView.as_view(), name='coupon-apply'),
    path('order/stripe-checkout/<str:order_oid>/', views.StripeCheckoutAPIView.as_view(), name='stripe-checkout'),
    path('order/payment-success/<str:order_oid>/', views.PaymentSuccessAPIView.as_view(), name='payment-success'),
    path('order/stripe/webhook/', views.StripeWebhookAPIView.as_view(), name='stripe-webhook'),
    # Frontend compatibility alias
    path('payment/payment-sucess/', views.PaymentSuccessAPIView.as_view(), name='payment-success-compat'),

    # ============== Enrollments ==============
    path('student/enrollments/', views.EnrollmentListAPIView.as_view(), name='enrollment-list'),
    path('student/enrollments/<str:enrollment_id>/', views.EnrollmentDetailAPIView.as_view(), name='enrollment-detail'),
    path('student/course/<slug:course_slug>/', views.CourseEnrollmentAPIView.as_view(), name='course-enrollment'),
    path('student/enroll-free/<str:course_id>/', views.FreeEnrollAPIView.as_view(), name='free-enroll'),
    path('student/progress/<str:enrollment_id>/', views.LessonProgressUpdateAPIView.as_view(), name='progress-update'),
    # Frontend compatibility alias for student course list
    path('student/course-list/<int:user_id>/', views.EnrollmentListAPIView.as_view(), name='student-course-list-compat'),

    # ============== Q&A ==============
    path('qa/answer/<str:question_id>/', views.AnswerCreateAPIView.as_view(), name='answer-create'),

    # ============== Wishlist ==============
    path('wishlist/', views.WishlistListAPIView.as_view(), name='wishlist-list'),
    path('wishlist/toggle/<str:course_id>/', views.WishlistToggleAPIView.as_view(), name='wishlist-toggle'),
    path('wishlist/check/<str:course_id>/', views.WishlistCheckAPIView.as_view(), name='wishlist-check'),

    # ============== Notifications ==============
    path('notifications/', views.NotificationListAPIView.as_view(), name='notification-list'),
    path('notifications/mark-read/', views.NotificationMarkReadAPIView.as_view(), name='notification-mark-all-read'),
    path('notifications/mark-read/<int:notification_id>/', views.NotificationMarkReadAPIView.as_view(), name='notification-mark-read'),

    # ============== Instructor ==============
    path('instructor/dashboard/', views.InstructorDashboardAPIView.as_view(), name='instructor-dashboard'),
    path('instructor/courses/', views.InstructorCoursesManageAPIView.as_view(), name='instructor-courses-manage'),
    path('instructor/coupons/', views.InstructorCouponsAPIView.as_view(), name='instructor-coupons'),
    # Frontend compatibility alias for teacher course list
    path('teacher/course-lists/<int:teacher_id>/', views.InstructorCoursesManageAPIView.as_view(), name='teacher-course-list-compat'),
]
