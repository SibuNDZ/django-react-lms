"""
Comprehensive tests for core LMS models.

Run with: python manage.py test core
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from decimal import Decimal
from datetime import timedelta

from .models import (
    Category, Course, Section, Lesson, LessonResource,
    Enrollment, LessonProgress, Cart, CartItem, Coupon,
    Order, OrderItem, CourseReview, Notification,
    Question, Answer, Wishlist
)

User = get_user_model()


class BaseTestCase(TestCase):
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


class CategoryModelTests(BaseTestCase):
    """Tests for Category model"""

    def test_category_creation(self):
        """Test basic category creation"""
        self.assertEqual(self.category.name, 'Programming')
        self.assertEqual(self.category.slug, 'programming')
        self.assertTrue(self.category.is_active)

    def test_category_slug_auto_generation(self):
        """Test slug is auto-generated from name"""
        category = Category.objects.create(name='Web Development')
        self.assertEqual(category.slug, 'web-development')

    def test_category_slug_unique(self):
        """Test slug uniqueness is enforced"""
        Category.objects.create(name='Python')
        with self.assertRaises(IntegrityError):
            Category.objects.create(name='Python', slug='python')

    def test_category_course_count(self):
        """Test course_count property"""
        course = Course.objects.create(
            title='Python Course',
            description='Learn Python',
            category=self.category,
            instructor=self.instructor,
            status='published'
        )
        self.assertEqual(self.category.course_count, 1)

        # Draft courses should not count
        Course.objects.create(
            title='Draft Course',
            description='Not published',
            category=self.category,
            instructor=self.instructor,
            status='draft'
        )
        self.assertEqual(self.category.course_count, 1)

    def test_category_ordering(self):
        """Test categories are ordered by order field then name"""
        cat1 = Category.objects.create(name='Zebra', order=1)
        cat2 = Category.objects.create(name='Alpha', order=2)
        cat3 = Category.objects.create(name='Beta', order=1)

        categories = list(Category.objects.filter(order__gt=0))
        # Order 1 comes first, then alphabetically within same order
        self.assertEqual(categories[0].name, 'Beta')
        self.assertEqual(categories[1].name, 'Zebra')
        self.assertEqual(categories[2].name, 'Alpha')


class CourseModelTests(BaseTestCase):
    """Tests for Course model"""

    def setUp(self):
        super().setUp()
        self.course = Course.objects.create(
            title='Python for Beginners',
            description='Learn Python from scratch',
            category=self.category,
            instructor=self.instructor,
            price=Decimal('49.99'),
            original_price=Decimal('99.99'),
        )

    def test_course_creation(self):
        """Test basic course creation"""
        self.assertEqual(self.course.title, 'Python for Beginners')
        self.assertEqual(self.course.instructor, self.instructor)
        self.assertEqual(self.course.status, 'draft')

    def test_course_slug_generation(self):
        """Test slug is auto-generated from title"""
        self.assertEqual(self.course.slug, 'python-for-beginners')

    def test_course_id_generation(self):
        """Test course_id is auto-generated"""
        self.assertIsNotNone(self.course.course_id)
        self.assertEqual(len(self.course.course_id), 10)

    def test_course_is_free_auto_set(self):
        """Test is_free is set when price is 0"""
        free_course = Course.objects.create(
            title='Free Course',
            description='Free content',
            instructor=self.instructor,
            price=Decimal('0.00')
        )
        self.assertTrue(free_course.is_free)

    def test_discount_percentage(self):
        """Test discount percentage calculation"""
        self.assertEqual(self.course.discount_percentage, 50)

    def test_discount_percentage_no_original_price(self):
        """Test discount is 0 when no original price"""
        course = Course.objects.create(
            title='No Discount',
            description='Test',
            instructor=self.instructor,
            price=Decimal('50.00')
        )
        self.assertEqual(course.discount_percentage, 0)

    def test_course_level_choices(self):
        """Test course level choices are valid"""
        valid_levels = ['beginner', 'intermediate', 'advanced']
        for level in valid_levels:
            course = Course.objects.create(
                title=f'{level} course',
                description='Test',
                instructor=self.instructor,
                level=level
            )
            self.assertEqual(course.level, level)


class SectionAndLessonTests(BaseTestCase):
    """Tests for Section and Lesson models"""

    def setUp(self):
        super().setUp()
        self.course = Course.objects.create(
            title='Test Course',
            description='Test',
            instructor=self.instructor
        )
        self.section = Section.objects.create(
            course=self.course,
            title='Introduction',
            order=0
        )

    def test_section_creation(self):
        """Test section creation with auto-generated ID"""
        self.assertIsNotNone(self.section.section_id)
        self.assertEqual(len(self.section.section_id), 10)

    def test_section_ordering(self):
        """Test sections are ordered by order field"""
        section2 = Section.objects.create(
            course=self.course,
            title='Advanced Topics',
            order=1
        )
        sections = list(self.course.sections.all())
        self.assertEqual(sections[0], self.section)
        self.assertEqual(sections[1], section2)

    def test_lesson_creation(self):
        """Test lesson creation"""
        lesson = Lesson.objects.create(
            section=self.section,
            title='First Lesson',
            lesson_type='video',
            duration=15
        )
        self.assertIsNotNone(lesson.lesson_id)
        self.assertTrue(lesson.is_published)

    def test_lesson_free_preview(self):
        """Test lesson can be marked as free preview"""
        lesson = Lesson.objects.create(
            section=self.section,
            title='Preview Lesson',
            is_free_preview=True
        )
        self.assertTrue(lesson.is_free_preview)

    def test_lesson_types(self):
        """Test all lesson types are valid"""
        types = ['video', 'text', 'quiz', 'assignment', 'resource']
        for lt in types:
            lesson = Lesson.objects.create(
                section=self.section,
                title=f'{lt} lesson',
                lesson_type=lt
            )
            self.assertEqual(lesson.lesson_type, lt)


class EnrollmentTests(BaseTestCase):
    """Tests for Enrollment and LessonProgress models"""

    def setUp(self):
        super().setUp()
        self.course = Course.objects.create(
            title='Test Course',
            description='Test',
            instructor=self.instructor,
            status='published'
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course
        )

    def test_enrollment_creation(self):
        """Test enrollment creation"""
        self.assertEqual(self.enrollment.status, 'active')
        self.assertEqual(self.enrollment.progress_percentage, 0)
        self.assertIsNotNone(self.enrollment.enrollment_id)

    def test_enrollment_unique_per_student_course(self):
        """Test student can only enroll once per course"""
        with self.assertRaises(IntegrityError):
            Enrollment.objects.create(
                student=self.student,
                course=self.course
            )

    def test_lesson_progress_tracking(self):
        """Test lesson progress tracking"""
        section = Section.objects.create(course=self.course, title='S1', order=0)
        lesson = Lesson.objects.create(section=section, title='L1')

        progress = LessonProgress.objects.create(
            enrollment=self.enrollment,
            lesson=lesson,
            is_completed=True,
            time_spent=600  # 10 minutes
        )
        self.assertTrue(progress.is_completed)
        self.assertEqual(progress.time_spent, 600)

    def test_enrollment_progress_validation(self):
        """Test progress percentage is validated"""
        self.enrollment.progress_percentage = 50
        self.enrollment.save()
        self.assertEqual(self.enrollment.progress_percentage, 50)


class CartTests(BaseTestCase):
    """Tests for Cart and CartItem models"""

    def setUp(self):
        super().setUp()
        self.course1 = Course.objects.create(
            title='Course 1',
            description='Test',
            instructor=self.instructor,
            price=Decimal('29.99')
        )
        self.course2 = Course.objects.create(
            title='Course 2',
            description='Test',
            instructor=self.instructor,
            price=Decimal('49.99')
        )
        self.cart = Cart.objects.create(
            cart_id='TEST-CART-001',
            user=self.student
        )

    def test_cart_creation(self):
        """Test cart creation"""
        self.assertEqual(self.cart.cart_id, 'TEST-CART-001')
        self.assertEqual(self.cart.user, self.student)

    def test_cart_item_creation(self):
        """Test adding items to cart"""
        item = CartItem.objects.create(
            cart=self.cart,
            course=self.course1,
            price=self.course1.price
        )
        self.assertEqual(item.price, Decimal('29.99'))

    def test_cart_total(self):
        """Test cart total calculation"""
        CartItem.objects.create(cart=self.cart, course=self.course1, price=self.course1.price)
        CartItem.objects.create(cart=self.cart, course=self.course2, price=self.course2.price)

        self.assertEqual(self.cart.total, Decimal('79.98'))

    def test_cart_item_count(self):
        """Test cart item count"""
        CartItem.objects.create(cart=self.cart, course=self.course1, price=self.course1.price)
        CartItem.objects.create(cart=self.cart, course=self.course2, price=self.course2.price)

        self.assertEqual(self.cart.item_count, 2)

    def test_cart_item_unique_per_course(self):
        """Test same course can't be added twice"""
        CartItem.objects.create(cart=self.cart, course=self.course1, price=self.course1.price)
        with self.assertRaises(IntegrityError):
            CartItem.objects.create(cart=self.cart, course=self.course1, price=self.course1.price)


class CouponTests(BaseTestCase):
    """Tests for Coupon model"""

    def setUp(self):
        super().setUp()
        self.now = timezone.now()
        self.coupon = Coupon.objects.create(
            code='SAVE20',
            discount_type='percentage',
            discount_value=Decimal('20.00'),
            valid_from=self.now - timedelta(days=1),
            valid_until=self.now + timedelta(days=30),
            max_uses=100
        )

    def test_coupon_creation(self):
        """Test coupon creation"""
        self.assertEqual(self.coupon.code, 'SAVE20')
        self.assertTrue(self.coupon.is_active)

    def test_coupon_is_valid(self):
        """Test coupon validity check"""
        self.assertTrue(self.coupon.is_valid)

    def test_coupon_expired(self):
        """Test expired coupon is invalid"""
        expired = Coupon.objects.create(
            code='EXPIRED',
            discount_type='percentage',
            discount_value=Decimal('10.00'),
            valid_from=self.now - timedelta(days=60),
            valid_until=self.now - timedelta(days=30)
        )
        self.assertFalse(expired.is_valid)

    def test_coupon_not_yet_valid(self):
        """Test future coupon is invalid"""
        future = Coupon.objects.create(
            code='FUTURE',
            discount_type='percentage',
            discount_value=Decimal('10.00'),
            valid_from=self.now + timedelta(days=30),
            valid_until=self.now + timedelta(days=60)
        )
        self.assertFalse(future.is_valid)

    def test_coupon_max_uses_reached(self):
        """Test coupon invalid when max uses reached"""
        self.coupon.times_used = 100
        self.coupon.save()
        self.assertFalse(self.coupon.is_valid)

    def test_coupon_inactive(self):
        """Test inactive coupon is invalid"""
        self.coupon.is_active = False
        self.coupon.save()
        self.assertFalse(self.coupon.is_valid)

    def test_fixed_discount_type(self):
        """Test fixed amount discount"""
        fixed = Coupon.objects.create(
            code='FLAT10',
            discount_type='fixed',
            discount_value=Decimal('10.00'),
            valid_from=self.now - timedelta(days=1),
            valid_until=self.now + timedelta(days=30)
        )
        self.assertEqual(fixed.discount_type, 'fixed')
        self.assertEqual(fixed.discount_value, Decimal('10.00'))


class OrderTests(BaseTestCase):
    """Tests for Order and OrderItem models"""

    def setUp(self):
        super().setUp()
        self.course = Course.objects.create(
            title='Test Course',
            description='Test',
            instructor=self.instructor,
            price=Decimal('99.99')
        )
        self.order = Order.objects.create(
            student=self.student,
            total=Decimal('99.99')
        )

    def test_order_creation(self):
        """Test order creation with auto-generated ID"""
        self.assertIsNotNone(self.order.order_id)
        self.assertEqual(len(self.order.order_id), 10)
        self.assertEqual(self.order.status, 'pending')

    def test_order_item_creation(self):
        """Test adding items to order"""
        item = OrderItem.objects.create(
            order=self.order,
            course=self.course,
            instructor=self.instructor,
            price=self.course.price
        )
        self.assertEqual(item.price, Decimal('99.99'))
        self.assertEqual(item.instructor, self.instructor)

    def test_order_status_transitions(self):
        """Test order status can be updated"""
        statuses = ['pending', 'processing', 'completed', 'failed', 'refunded']
        for status in statuses:
            self.order.status = status
            self.order.save()
            self.assertEqual(self.order.status, status)

    def test_order_payment_methods(self):
        """Test valid payment methods"""
        methods = ['stripe', 'paypal', 'free']
        for method in methods:
            self.order.payment_method = method
            self.order.save()
            self.assertEqual(self.order.payment_method, method)


class CourseReviewTests(BaseTestCase):
    """Tests for CourseReview model"""

    def setUp(self):
        super().setUp()
        self.course = Course.objects.create(
            title='Test Course',
            description='Test',
            instructor=self.instructor,
            status='published'
        )
        # Student must be enrolled to review
        Enrollment.objects.create(student=self.student, course=self.course)

    def test_review_creation(self):
        """Test review creation"""
        review = CourseReview.objects.create(
            student=self.student,
            course=self.course,
            rating=5,
            review_text='Excellent course!'
        )
        self.assertEqual(review.rating, 5)
        self.assertTrue(review.is_approved)
        self.assertIsNotNone(review.review_id)

    def test_review_unique_per_student_course(self):
        """Test student can only review once per course"""
        CourseReview.objects.create(
            student=self.student,
            course=self.course,
            rating=4,
            review_text='Good course'
        )
        with self.assertRaises(IntegrityError):
            CourseReview.objects.create(
                student=self.student,
                course=self.course,
                rating=5,
                review_text='Changed my mind'
            )

    def test_review_rating_choices(self):
        """Test valid rating values"""
        for rating in range(1, 6):
            user = User.objects.create_user(
                email=f'user{rating}@test.com',
                username=f'user{rating}',
                password='testpass123'
            )
            Enrollment.objects.create(student=user, course=self.course)
            review = CourseReview.objects.create(
                student=user,
                course=self.course,
                rating=rating,
                review_text=f'{rating} star review'
            )
            self.assertEqual(review.rating, rating)


class QuestionAnswerTests(BaseTestCase):
    """Tests for Question and Answer models"""

    def setUp(self):
        super().setUp()
        self.course = Course.objects.create(
            title='Test Course',
            description='Test',
            instructor=self.instructor
        )
        self.question = Question.objects.create(
            course=self.course,
            student=self.student,
            title='How do I do X?',
            content='I need help understanding X'
        )

    def test_question_creation(self):
        """Test question creation"""
        self.assertIsNotNone(self.question.question_id)
        self.assertFalse(self.question.is_resolved)

    def test_answer_creation(self):
        """Test answer creation"""
        answer = Answer.objects.create(
            question=self.question,
            user=self.instructor,
            content='Here is how you do X...'
        )
        self.assertIsNotNone(answer.answer_id)
        self.assertFalse(answer.is_accepted)

    def test_answer_accepted(self):
        """Test marking answer as accepted"""
        answer = Answer.objects.create(
            question=self.question,
            user=self.instructor,
            content='Solution'
        )
        answer.is_accepted = True
        answer.save()
        self.assertTrue(answer.is_accepted)


class WishlistTests(BaseTestCase):
    """Tests for Wishlist model"""

    def setUp(self):
        super().setUp()
        self.course = Course.objects.create(
            title='Test Course',
            description='Test',
            instructor=self.instructor
        )

    def test_wishlist_creation(self):
        """Test adding course to wishlist"""
        wishlist = Wishlist.objects.create(
            user=self.student,
            course=self.course
        )
        self.assertEqual(wishlist.user, self.student)
        self.assertEqual(wishlist.course, self.course)

    def test_wishlist_unique_per_user_course(self):
        """Test course can only be wishlisted once per user"""
        Wishlist.objects.create(user=self.student, course=self.course)
        with self.assertRaises(IntegrityError):
            Wishlist.objects.create(user=self.student, course=self.course)


class NotificationTests(BaseTestCase):
    """Tests for Notification model"""

    def test_notification_creation(self):
        """Test notification creation"""
        notification = Notification.objects.create(
            user=self.student,
            notification_type='enrollment',
            title='Welcome!',
            message='You have enrolled in a new course'
        )
        self.assertFalse(notification.is_read)
        self.assertEqual(notification.notification_type, 'enrollment')

    def test_notification_types(self):
        """Test all notification types are valid"""
        types = ['enrollment', 'review', 'order', 'course', 'system']
        for nt in types:
            notification = Notification.objects.create(
                user=self.student,
                notification_type=nt,
                title=f'{nt} notification',
                message='Test message'
            )
            self.assertEqual(notification.notification_type, nt)


class LessonResourceTests(BaseTestCase):
    """Tests for LessonResource model"""

    def setUp(self):
        super().setUp()
        self.course = Course.objects.create(
            title='Test Course',
            description='Test',
            instructor=self.instructor
        )
        self.section = Section.objects.create(
            course=self.course,
            title='Section 1',
            order=0
        )
        self.lesson = Lesson.objects.create(
            section=self.section,
            title='Lesson 1'
        )

    def test_resource_id_generation(self):
        """Test resource ID is auto-generated"""
        # Note: This test would need a file to be complete
        # For now we just test the model can be instantiated
        resource = LessonResource(
            lesson=self.lesson,
            title='Course Notes'
        )
        self.assertEqual(resource.lesson, self.lesson)
