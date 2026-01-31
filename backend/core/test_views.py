"""
API tests for core LMS views.

Run with: python manage.py test core.test_views
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from decimal import Decimal
from datetime import timedelta
import json

from .models import (
    Category, Course, Section, Lesson,
    Enrollment, LessonProgress, Cart, CartItem, Coupon,
    Order, OrderItem, CourseReview, Question, Answer, Wishlist
)

User = get_user_model()


class BaseAPITestCase(APITestCase):
    """Base test case with common setup"""

    def setUp(self):
        """Create test users and common objects"""
        self.instructor = User.objects.create_user(
            email='instructor@test.com',
            username='instructor',
            password='testpass123'
        )
        self.student = User.objects.create_user(
            email='student@test.com',
            username='student',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Programming',
            description='Programming courses'
        )
        self.course = Course.objects.create(
            title='Python Basics',
            description='Learn Python',
            category=self.category,
            instructor=self.instructor,
            price=Decimal('49.99'),
            status='published'
        )
        self.section = Section.objects.create(
            course=self.course,
            title='Introduction',
            order=0
        )
        self.lesson = Lesson.objects.create(
            section=self.section,
            title='Getting Started',
            lesson_type='video',
            duration=15,
            is_free_preview=True
        )

    def authenticate_as_student(self):
        """Authenticate as the test student"""
        self.client.force_authenticate(user=self.student)

    def authenticate_as_instructor(self):
        """Authenticate as the test instructor"""
        self.client.force_authenticate(user=self.instructor)


class CategoryAPITests(BaseAPITestCase):
    """Tests for Category API endpoints"""

    def test_list_categories(self):
        """Test listing all active categories"""
        response = self.client.get('/api/v1/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Programming')

    def test_category_detail(self):
        """Test getting category details by slug"""
        response = self.client.get(f'/api/v1/categories/{self.category.slug}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Programming')

    def test_inactive_category_hidden(self):
        """Test that inactive categories are not listed"""
        self.category.is_active = False
        self.category.save()
        response = self.client.get('/api/v1/categories/')
        self.assertEqual(len(response.data), 0)


class CourseAPITests(BaseAPITestCase):
    """Tests for Course API endpoints"""

    def test_list_courses(self):
        """Test listing published courses"""
        response = self.client.get('/api/v1/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)

    def test_draft_course_not_listed(self):
        """Test that draft courses are not listed"""
        self.course.status = 'draft'
        self.course.save()
        response = self.client.get('/api/v1/courses/')
        self.assertEqual(len(response.data['results']), 0)

    def test_course_detail(self):
        """Test getting course details by slug"""
        response = self.client.get(f'/api/v1/courses/{self.course.slug}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Python Basics')

    def test_filter_by_category(self):
        """Test filtering courses by category"""
        response = self.client.get(f'/api/v1/courses/?category={self.category.slug}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_filter_by_level(self):
        """Test filtering courses by level"""
        response = self.client.get('/api/v1/courses/?level=beginner')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_search_courses(self):
        """Test course search"""
        response = self.client.get('/api/v1/courses/search/?q=Python')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_search_no_results(self):
        """Test search with no matching results"""
        response = self.client.get('/api/v1/courses/search/?q=nonexistent')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_featured_courses(self):
        """Test getting featured courses"""
        self.course.is_featured = True
        self.course.save()
        response = self.client.get('/api/v1/courses/featured/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class CartAPITests(BaseAPITestCase):
    """Tests for Cart API endpoints"""

    def test_get_empty_cart_anonymous(self):
        """Test getting cart for anonymous user"""
        response = self.client.get('/api/v1/cart/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['item_count'], 0)

    def test_get_cart_authenticated(self):
        """Test getting cart for authenticated user"""
        self.authenticate_as_student()
        response = self.client.get('/api/v1/cart/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_to_cart(self):
        """Test adding course to cart"""
        self.authenticate_as_student()
        response = self.client.post('/api/v1/cart/add/', {
            'course_id': self.course.course_id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('cart_id', response.data)

    def test_add_duplicate_to_cart(self):
        """Test adding same course twice"""
        self.authenticate_as_student()
        self.client.post('/api/v1/cart/add/', {'course_id': self.course.course_id})
        response = self.client.post('/api/v1/cart/add/', {'course_id': self.course.course_id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_enrolled_course_to_cart(self):
        """Test adding already enrolled course fails"""
        self.authenticate_as_student()
        Enrollment.objects.create(student=self.student, course=self.course)
        response = self.client.post('/api/v1/cart/add/', {'course_id': self.course.course_id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_remove_from_cart(self):
        """Test removing course from cart"""
        cart = Cart.objects.create(cart_id='test-cart', user=self.student)
        CartItem.objects.create(cart=cart, course=self.course, price=self.course.price)

        self.authenticate_as_student()
        response = self.client.delete(f'/api/v1/cart/{cart.cart_id}/remove/{self.course.course_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_clear_cart(self):
        """Test clearing cart"""
        cart = Cart.objects.create(cart_id='test-cart', user=self.student)
        CartItem.objects.create(cart=cart, course=self.course, price=self.course.price)

        response = self.client.delete(f'/api/v1/cart/{cart.cart_id}/clear/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(cart.items.count(), 0)


class OrderAPITests(BaseAPITestCase):
    """Tests for Order API endpoints"""

    def setUp(self):
        super().setUp()
        self.cart = Cart.objects.create(cart_id='test-cart', user=self.student)
        CartItem.objects.create(cart=self.cart, course=self.course, price=self.course.price)

    def test_create_order_unauthenticated(self):
        """Test order creation requires authentication"""
        response = self.client.post('/api/v1/order/create/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order(self):
        """Test creating order from cart"""
        self.authenticate_as_student()
        response = self.client.post('/api/v1/order/create/', {
            'cart_id': self.cart.cart_id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('order_id', response.data)

    def test_create_order_empty_cart(self):
        """Test creating order with empty cart fails"""
        self.cart.items.all().delete()
        self.authenticate_as_student()
        response = self.client.post('/api/v1/order/create/', {
            'cart_id': self.cart.cart_id
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_orders(self):
        """Test listing user's orders"""
        Order.objects.create(student=self.student, total=Decimal('49.99'))
        self.authenticate_as_student()
        response = self.client.get('/api/v1/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class CouponAPITests(BaseAPITestCase):
    """Tests for Coupon API endpoints"""

    def setUp(self):
        super().setUp()
        self.order = Order.objects.create(
            student=self.student,
            subtotal=Decimal('49.99'),
            total=Decimal('49.99')
        )
        now = timezone.now()
        self.coupon = Coupon.objects.create(
            code='SAVE20',
            discount_type='percentage',
            discount_value=Decimal('20'),
            valid_from=now - timedelta(days=1),
            valid_until=now + timedelta(days=30)
        )

    def test_apply_coupon(self):
        """Test applying valid coupon to order"""
        self.authenticate_as_student()
        response = self.client.post('/api/v1/coupon/apply/', {
            'order_oid': self.order.order_id,
            'coupon_code': 'SAVE20'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('discount', response.data)

    def test_apply_invalid_coupon(self):
        """Test applying non-existent coupon"""
        self.authenticate_as_student()
        response = self.client.post('/api/v1/coupon/apply/', {
            'order_oid': self.order.order_id,
            'coupon_code': 'INVALID'
        })
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_apply_expired_coupon(self):
        """Test applying expired coupon"""
        self.coupon.valid_until = timezone.now() - timedelta(days=1)
        self.coupon.save()
        self.authenticate_as_student()
        response = self.client.post('/api/v1/coupon/apply/', {
            'order_oid': self.order.order_id,
            'coupon_code': 'SAVE20'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class EnrollmentAPITests(BaseAPITestCase):
    """Tests for Enrollment API endpoints"""

    def setUp(self):
        super().setUp()
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course
        )

    def test_list_enrollments(self):
        """Test listing user's enrollments"""
        self.authenticate_as_student()
        response = self.client.get('/api/v1/enrollments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_enrollment_detail(self):
        """Test getting enrollment details"""
        self.authenticate_as_student()
        response = self.client.get(f'/api/v1/enrollment/{self.enrollment.enrollment_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['course']['title'], 'Python Basics')

    def test_enroll_free_course(self):
        """Test enrolling in free course"""
        free_course = Course.objects.create(
            title='Free Course',
            description='Free',
            instructor=self.instructor,
            price=Decimal('0'),
            status='published'
        )
        self.authenticate_as_student()
        response = self.client.post(f'/api/v1/enroll/free/{free_course.course_id}/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_enroll_paid_course_as_free(self):
        """Test enrolling in paid course as free fails"""
        self.authenticate_as_student()
        response = self.client.post(f'/api/v1/enroll/free/{self.course.course_id}/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LessonProgressAPITests(BaseAPITestCase):
    """Tests for lesson progress tracking"""

    def setUp(self):
        super().setUp()
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course
        )
        # Update course total lessons
        self.course.total_lessons = 1
        self.course.save()

    def test_update_lesson_progress(self):
        """Test updating lesson progress"""
        self.authenticate_as_student()
        response = self.client.post(
            f'/api/v1/enrollment/{self.enrollment.enrollment_id}/progress/',
            {
                'lesson_id': self.lesson.lesson_id,
                'is_completed': True,
                'time_spent': 600
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['lessons_completed'], 1)

    def test_progress_updates_enrollment_percentage(self):
        """Test that completing lessons updates enrollment progress"""
        self.authenticate_as_student()
        self.client.post(
            f'/api/v1/enrollment/{self.enrollment.enrollment_id}/progress/',
            {'lesson_id': self.lesson.lesson_id, 'is_completed': True}
        )
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.progress_percentage, 100)


class ReviewAPITests(BaseAPITestCase):
    """Tests for Course Review API endpoints"""

    def setUp(self):
        super().setUp()
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course
        )

    def test_list_reviews(self):
        """Test listing course reviews"""
        CourseReview.objects.create(
            student=self.student,
            course=self.course,
            rating=5,
            review_text='Great course!'
        )
        response = self.client.get(f'/api/v1/courses/{self.course.slug}/reviews/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_review(self):
        """Test creating a review"""
        self.authenticate_as_student()
        response = self.client.post(
            f'/api/v1/courses/{self.course.slug}/review/',
            {'rating': 5, 'review_text': 'Excellent!'}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_review_without_enrollment(self):
        """Test that non-enrolled users cannot review"""
        self.enrollment.delete()
        self.authenticate_as_student()
        response = self.client.post(
            f'/api/v1/courses/{self.course.slug}/review/',
            {'rating': 5, 'review_text': 'Excellent!'}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_review(self):
        """Test updating an existing review"""
        CourseReview.objects.create(
            student=self.student,
            course=self.course,
            rating=4,
            review_text='Good'
        )
        self.authenticate_as_student()
        response = self.client.post(
            f'/api/v1/courses/{self.course.slug}/review/',
            {'rating': 5, 'review_text': 'Actually excellent!'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 5)


class QAAPITests(BaseAPITestCase):
    """Tests for Q&A API endpoints"""

    def setUp(self):
        super().setUp()
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course
        )

    def test_list_questions(self):
        """Test listing course questions"""
        Question.objects.create(
            course=self.course,
            student=self.student,
            title='How to X?',
            content='I need help'
        )
        response = self.client.get(f'/api/v1/courses/{self.course.slug}/qa/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_ask_question(self):
        """Test asking a question"""
        self.authenticate_as_student()
        response = self.client.post(
            f'/api/v1/courses/{self.course.slug}/question/',
            {'title': 'Question?', 'content': 'Details'}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_answer_question(self):
        """Test answering a question"""
        question = Question.objects.create(
            course=self.course,
            student=self.student,
            title='Question?',
            content='Details'
        )
        self.authenticate_as_instructor()
        response = self.client.post(
            f'/api/v1/question/{question.question_id}/answer/',
            {'content': 'Here is the answer'}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class WishlistAPITests(BaseAPITestCase):
    """Tests for Wishlist API endpoints"""

    def test_list_wishlist(self):
        """Test listing wishlist"""
        Wishlist.objects.create(user=self.student, course=self.course)
        self.authenticate_as_student()
        response = self.client.get('/api/v1/wishlist/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_toggle_wishlist_add(self):
        """Test adding to wishlist"""
        self.authenticate_as_student()
        response = self.client.post(f'/api/v1/wishlist/toggle/{self.course.course_id}/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['in_wishlist'])

    def test_toggle_wishlist_remove(self):
        """Test removing from wishlist"""
        Wishlist.objects.create(user=self.student, course=self.course)
        self.authenticate_as_student()
        response = self.client.post(f'/api/v1/wishlist/toggle/{self.course.course_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['in_wishlist'])

    def test_check_wishlist(self):
        """Test checking if course is in wishlist"""
        Wishlist.objects.create(user=self.student, course=self.course)
        self.authenticate_as_student()
        response = self.client.get(f'/api/v1/wishlist/check/{self.course.course_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['in_wishlist'])


class InstructorDashboardAPITests(BaseAPITestCase):
    """Tests for Instructor Dashboard API"""

    def test_dashboard_stats(self):
        """Test instructor dashboard statistics"""
        self.authenticate_as_instructor()
        response = self.client.get('/api/v1/instructor/dashboard/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_courses', response.data)
        self.assertIn('total_students', response.data)
        self.assertIn('total_earnings', response.data)

    def test_instructor_courses(self):
        """Test listing instructor's courses"""
        self.authenticate_as_instructor()
        response = self.client.get('/api/v1/instructor/courses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class HealthCheckAPITests(APITestCase):
    """Tests for health check endpoints"""

    def test_basic_health_check(self):
        """Test basic liveness check"""
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'healthy')

    def test_readiness_check(self):
        """Test readiness check"""
        response = self.client.get('/health/ready/')
        # Should return 200 when DB is available (in test environment)
        self.assertIn(response.status_code, [200, 503])
        self.assertIn('checks', response.data)
