"""
Core LMS API Views

This module contains all the API endpoints for:
- Course browsing and searching
- Shopping cart management
- Order and checkout processing
- Student enrollment and progress tracking
- Reviews and Q&A
- Wishlist management
"""

from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg, Sum
from django.utils import timezone
from django.conf import settings

from rest_framework import generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination

import stripe
import logging
import shortuuid

from .models import (
    Category, Course, Section, Lesson, LessonResource,
    Enrollment, LessonProgress, Cart, CartItem, Coupon,
    Order, OrderItem, CourseReview, Notification, Question, Answer, Wishlist
)
from api.serializer import (
    CategorySerializer, CourseListSerializer, CourseDetailSerializer,
    CourseEnrolledSerializer, LessonSerializer,
    CartSerializer, CartItemCreateSerializer,
    OrderSerializer, CouponApplySerializer,
    EnrollmentSerializer, EnrollmentDetailSerializer,
    LessonProgressUpdateSerializer,
    CourseReviewSerializer, CourseReviewCreateSerializer,
    QuestionSerializer, QuestionCreateSerializer,
    AnswerSerializer, AnswerCreateSerializer,
    WishlistSerializer, NotificationSerializer, CouponSerializer
)

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')


# ============== Pagination ==============

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


# ============== Category Views ==============

class CategoryListAPIView(generics.ListAPIView):
    """
    List all active categories.

    Returns categories with their course counts.
    """
    queryset = Category.objects.filter(is_active=True).order_by('order', 'name')
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class CategoryDetailAPIView(generics.RetrieveAPIView):
    """
    Get category details by slug.
    """
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'


# ============== Course Views ==============

class CourseListAPIView(generics.ListAPIView):
    """
    List all published courses with pagination.

    Supports filtering by:
    - category (slug)
    - level (beginner, intermediate, advanced)
    - is_free (true/false)
    - price_min, price_max

    Supports ordering by:
    - created_at, -created_at
    - price, -price
    - average_rating, -average_rating
    - total_students, -total_students
    """
    serializer_class = CourseListSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'short_description', 'tags']
    ordering_fields = ['created_at', 'price', 'average_rating', 'total_students']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Course.objects.filter(status='published').select_related(
            'instructor', 'category'
        )

        # Category filter
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)

        # Level filter
        level = self.request.query_params.get('level')
        if level:
            queryset = queryset.filter(level=level)

        # Free filter
        is_free = self.request.query_params.get('is_free')
        if is_free is not None:
            queryset = queryset.filter(is_free=is_free.lower() == 'true')

        # Price range filter
        price_min = self.request.query_params.get('price_min')
        price_max = self.request.query_params.get('price_max')
        if price_min:
            queryset = queryset.filter(price__gte=price_min)
        if price_max:
            queryset = queryset.filter(price__lte=price_max)

        # Language filter
        language = self.request.query_params.get('language')
        if language:
            queryset = queryset.filter(language=language)

        return queryset


class FeaturedCourseListAPIView(generics.ListAPIView):
    """
    List featured courses (for homepage).
    """
    serializer_class = CourseListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Course.objects.filter(
            status='published', is_featured=True
        ).select_related('instructor', 'category')[:8]


class CourseDetailAPIView(generics.RetrieveAPIView):
    """
    Get course details by slug.

    Returns full course information including curriculum.
    Video URLs are hidden for non-enrolled users (except free previews).
    """
    queryset = Course.objects.filter(status='published').select_related(
        'instructor', 'category'
    ).prefetch_related('sections__lessons')
    serializer_class = CourseDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'


class CourseSearchAPIView(generics.ListAPIView):
    """
    Search courses by title, description, or tags.
    """
    serializer_class = CourseListSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        if not query:
            return Course.objects.none()

        return Course.objects.filter(
            Q(status='published') &
            (Q(title__icontains=query) |
             Q(short_description__icontains=query) |
             Q(description__icontains=query) |
             Q(tags__icontains=query))
        ).select_related('instructor', 'category')


class InstructorPublicCoursesAPIView(generics.ListAPIView):
    """
    List published courses by a specific instructor.
    """
    serializer_class = CourseListSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        instructor_id = self.kwargs.get('instructor_id')
        return Course.objects.filter(
            instructor_id=instructor_id, status='published'
        ).select_related('instructor', 'category')


# ============== Cart Views ==============

class CartAPIView(APIView):
    """
    Get or create shopping cart.

    For authenticated users: cart is linked to user account.
    For anonymous users: cart is identified by cart_id cookie/param.
    """
    permission_classes = [AllowAny]

    def get(self, request, cart_id=None):
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(
                user=request.user,
                defaults={'cart_id': shortuuid.uuid()}
            )
        elif cart_id:
            cart = get_object_or_404(Cart, cart_id=cart_id)
        else:
            return Response(
                {"items": [], "total": 0, "item_count": 0},
                status=status.HTTP_200_OK
            )

        serializer = CartSerializer(cart)
        return Response(serializer.data)


class CartItemAddAPIView(APIView):
    """
    Add a course to the shopping cart.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CartItemCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course_id = serializer.validated_data['course_id']
        cart_id = serializer.validated_data.get('cart_id')

        # Get the course
        course = get_object_or_404(Course, course_id=course_id, status='published')

        # Check if user already enrolled
        if request.user.is_authenticated:
            if Enrollment.objects.filter(student=request.user, course=course).exists():
                return Response(
                    {"message": "You are already enrolled in this course"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Get or create cart
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(
                user=request.user,
                defaults={'cart_id': shortuuid.uuid()}
            )
        elif cart_id:
            cart, _ = Cart.objects.get_or_create(
                cart_id=cart_id,
                defaults={'cart_id': cart_id}
            )
        else:
            cart = Cart.objects.create(cart_id=shortuuid.uuid())

        # Check if course already in cart
        if CartItem.objects.filter(cart=cart, course=course).exists():
            return Response(
                {"message": "Course already in cart"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Add to cart
        CartItem.objects.create(cart=cart, course=course, price=course.price)

        logger.info(f"Course {course.title} added to cart {cart.cart_id}")
        return Response(
            {"message": "Course added to cart", "cart_id": cart.cart_id},
            status=status.HTTP_201_CREATED
        )


class CartItemRemoveAPIView(APIView):
    """
    Remove a course from the shopping cart.
    """
    permission_classes = [AllowAny]

    def delete(self, request, cart_id, course_id):
        cart = get_object_or_404(Cart, cart_id=cart_id)
        course = get_object_or_404(Course, course_id=course_id)

        deleted, _ = CartItem.objects.filter(cart=cart, course=course).delete()

        if deleted:
            return Response({"message": "Item removed from cart"})
        return Response(
            {"message": "Item not found in cart"},
            status=status.HTTP_404_NOT_FOUND
        )


class CartClearAPIView(APIView):
    """
    Clear all items from the cart.
    """
    permission_classes = [AllowAny]

    def delete(self, request, cart_id):
        cart = get_object_or_404(Cart, cart_id=cart_id)
        cart.items.all().delete()
        return Response({"message": "Cart cleared"})


class CartStatsAPIView(APIView):
    """
    Get cart statistics (count and total).
    """
    permission_classes = [AllowAny]

    def get(self, request, cart_id=None):
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        elif cart_id:
            cart = Cart.objects.filter(cart_id=cart_id).first()
        else:
            return Response({"count": 0, "total": 0})

        if not cart:
            return Response({"count": 0, "total": 0})

        return Response({
            "count": cart.item_count,
            "total": float(cart.total)
        })


# ============== Order Views ==============

class OrderCreateAPIView(APIView):
    """
    Create an order from the shopping cart.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart_id = request.data.get('cart_id')

        # Get cart
        if cart_id:
            cart = get_object_or_404(Cart, cart_id=cart_id)
        else:
            cart = Cart.objects.filter(user=request.user).first()

        if not cart or cart.item_count == 0:
            return Response(
                {"message": "Cart is empty"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check for already enrolled courses
        for item in cart.items.all():
            if Enrollment.objects.filter(student=request.user, course=item.course).exists():
                return Response(
                    {"message": f"You are already enrolled in {item.course.title}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Create order
        order = Order.objects.create(
            student=request.user,
            subtotal=cart.total,
            total=cart.total
        )

        # Create order items
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                course=item.course,
                instructor=item.course.instructor,
                price=item.price
            )

        logger.info(f"Order {order.order_id} created for user {request.user.email}")

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderDetailAPIView(generics.RetrieveAPIView):
    """
    Get order details for checkout.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'order_id'
    lookup_url_kwarg = 'order_oid'

    def get_queryset(self):
        return Order.objects.filter(student=self.request.user)


class OrderListAPIView(generics.ListAPIView):
    """
    List user's orders.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Order.objects.filter(student=self.request.user).order_by('-created_at')


class CouponApplyAPIView(APIView):
    """
    Apply a coupon code to an order.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CouponApplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_oid = serializer.validated_data['order_oid']
        coupon_code = serializer.validated_data['coupon_code']

        order = get_object_or_404(Order, order_id=order_oid, student=request.user)

        if order.status != 'pending':
            return Response(
                {"message": "Cannot apply coupon to this order", "icon": "error"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            coupon = Coupon.objects.get(code__iexact=coupon_code)
        except Coupon.DoesNotExist:
            return Response(
                {"message": "Coupon not found", "icon": "error"},
                status=status.HTTP_404_NOT_FOUND
            )

        if not coupon.is_valid:
            return Response(
                {"message": "Coupon is not valid or has expired", "icon": "error"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate discount
        if coupon.discount_type == 'percentage':
            discount = (order.subtotal * coupon.discount_value) / 100
        else:
            discount = coupon.discount_value

        # Apply discount
        order.coupon = coupon
        order.discount = min(discount, order.subtotal)  # Don't exceed subtotal
        order.total = order.subtotal - order.discount
        order.save()

        logger.info(f"Coupon {coupon_code} applied to order {order_oid}")
        return Response({
            "message": "Coupon applied successfully",
            "icon": "success",
            "discount": float(order.discount),
            "total": float(order.total)
        })


class StripeCheckoutAPIView(APIView):
    """
    Create Stripe checkout session for payment.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, order_oid):
        order = get_object_or_404(Order, order_id=order_oid, student=request.user)

        if order.status != 'pending':
            return Response(
                {"message": "Order cannot be processed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Handle free orders
        if order.total == 0:
            return self.complete_free_order(order)

        try:
            checkout_session = stripe.checkout.Session.create(
                customer_email=request.user.email,
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f'Order #{order.order_id}',
                        },
                        'unit_amount': int(order.total * 100),  # Stripe uses cents
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f"{settings.FRONTEND_SITE_URL}/payment-success/?order_id={order.order_id}&session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.FRONTEND_SITE_URL}/checkout/{order.order_id}/",
                metadata={
                    'order_id': order.order_id,
                    'user_id': request.user.id,
                }
            )

            order.stripe_payment_intent = checkout_session.id
            order.status = 'processing'
            order.save()

            return Response({'checkout_url': checkout_session.url})

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            return Response(
                {"message": "Payment processing failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def complete_free_order(self, order):
        """Complete order for free courses."""
        order.status = 'completed'
        order.payment_method = 'free'
        order.completed_at = timezone.now()
        order.save()

        # Create enrollments
        self.create_enrollments(order)

        return Response({
            "message": "Order completed",
            "redirect_url": f"/payment-success/?order_id={order.order_id}"
        })

    def create_enrollments(self, order):
        """Create enrollments for all courses in the order."""
        for item in order.items.all():
            Enrollment.objects.get_or_create(
                student=order.student,
                course=item.course,
                defaults={'status': 'active'}
            )
            # Update course student count
            item.course.total_students += 1
            item.course.save(update_fields=['total_students'])


class PaymentSuccessAPIView(APIView):
    """
    Handle successful payment callback.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, order_oid=None):
        """Handle POST from frontend with order_oid in body."""
        order_oid = order_oid or request.data.get('order_oid')
        session_id = request.data.get('session_id')
        paypal_order_id = request.data.get('paypal_order_id')

        if not order_oid:
            return Response(
                {"message": "Order ID required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        order = get_object_or_404(Order, order_id=order_oid, student=request.user)

        if order.status == 'completed':
            return Response({"message": "Already Paid"})

        # Verify payment based on method
        payment_verified = False

        if session_id and session_id != 'null':
            try:
                session = stripe.checkout.Session.retrieve(session_id)
                if session.payment_status == 'paid':
                    payment_verified = True
                    order.payment_id = session.payment_intent
                    order.payment_method = 'stripe'
            except stripe.error.StripeError as e:
                logger.error(f"Stripe verification error: {str(e)}")

        if paypal_order_id and paypal_order_id != 'null':
            # For PayPal, accept the order_id (real verification would use PayPal SDK)
            payment_verified = True
            order.payment_id = paypal_order_id
            order.payment_method = 'paypal'

        if payment_verified:
            order.status = 'completed'
            order.completed_at = timezone.now()
            order.save()

            # Create enrollments
            for item in order.items.all():
                Enrollment.objects.get_or_create(
                    student=order.student,
                    course=item.course,
                    defaults={'status': 'active'}
                )
                item.course.total_students += 1
                item.course.save(update_fields=['total_students'])

            # Clear cart
            Cart.objects.filter(user=request.user).delete()

            # Send notification
            Notification.objects.create(
                user=request.user,
                notification_type='order',
                title='Order Completed',
                message=f'Your order #{order.order_id} has been completed. Enjoy your courses!',
                order=order
            )

            logger.info(f"Payment completed for order {order_oid}")
            return Response({"message": "Payment Successfull", "order": OrderSerializer(order).data})

        return Response(
            {"message": "Payment Failed"},
            status=status.HTTP_400_BAD_REQUEST
        )

    def get(self, request, order_oid):
        """Handle GET with order_oid in URL."""
        session_id = request.query_params.get('session_id')
        order = get_object_or_404(Order, order_id=order_oid, student=request.user)

        if order.status == 'completed':
            return Response({"message": "Already Paid"})

        if session_id:
            try:
                session = stripe.checkout.Session.retrieve(session_id)
                if session.payment_status == 'paid':
                    order.status = 'completed'
                    order.payment_id = session.payment_intent
                    order.payment_method = 'stripe'
                    order.completed_at = timezone.now()
                    order.save()

                    # Create enrollments
                    for item in order.items.all():
                        Enrollment.objects.get_or_create(
                            student=order.student,
                            course=item.course,
                            defaults={'status': 'active'}
                        )
                        item.course.total_students += 1
                        item.course.save(update_fields=['total_students'])

                    # Clear cart
                    Cart.objects.filter(user=request.user).delete()

                    # Send notification
                    Notification.objects.create(
                        user=request.user,
                        notification_type='order',
                        title='Order Completed',
                        message=f'Your order #{order.order_id} has been completed. Enjoy your courses!',
                        order=order
                    )

                    logger.info(f"Payment completed for order {order_oid}")
                    return Response({"message": "Payment Successfull", "order": OrderSerializer(order).data})
            except stripe.error.StripeError as e:
                logger.error(f"Stripe verification error: {str(e)}")

        return Response(
            {"message": "Payment Failed"},
            status=status.HTTP_400_BAD_REQUEST
        )


# ============== Enrollment Views ==============

class EnrollmentListAPIView(generics.ListAPIView):
    """
    List user's enrolled courses.
    """
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Enrollment.objects.filter(
            student=self.request.user
        ).select_related('course', 'course__instructor').order_by('-enrolled_at')


class EnrollmentDetailAPIView(generics.RetrieveAPIView):
    """
    Get enrollment details including full course content.
    """
    serializer_class = EnrollmentDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'enrollment_id'

    def get_queryset(self):
        return Enrollment.objects.filter(
            student=self.request.user
        ).select_related('course', 'course__instructor').prefetch_related(
            'course__sections__lessons', 'lesson_progress'
        )


class CourseEnrollmentAPIView(APIView):
    """
    Get enrollment for a specific course (or check if enrolled).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, course_slug):
        course = get_object_or_404(Course, slug=course_slug)
        enrollment = Enrollment.objects.filter(
            student=request.user, course=course
        ).first()

        if enrollment:
            # Update last accessed
            enrollment.last_accessed = timezone.now()
            enrollment.save(update_fields=['last_accessed'])

            serializer = EnrollmentDetailSerializer(enrollment)
            return Response(serializer.data)

        return Response(
            {"enrolled": False, "message": "Not enrolled in this course"},
            status=status.HTTP_404_NOT_FOUND
        )


class FreeEnrollAPIView(APIView):
    """
    Enroll in a free course directly.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id):
        course = get_object_or_404(Course, course_id=course_id, status='published')

        if not course.is_free:
            return Response(
                {"message": "This course is not free"},
                status=status.HTTP_400_BAD_REQUEST
            )

        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user,
            course=course,
            defaults={'status': 'active'}
        )

        if not created:
            return Response(
                {"message": "Already enrolled in this course"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update course student count
        course.total_students += 1
        course.save(update_fields=['total_students'])

        logger.info(f"User {request.user.email} enrolled in free course {course.title}")
        return Response(
            {"message": "Enrolled successfully", "enrollment_id": enrollment.enrollment_id},
            status=status.HTTP_201_CREATED
        )


# ============== Lesson & Progress Views ==============

class LessonDetailAPIView(APIView):
    """
    Get lesson details and content.
    Only returns full content for enrolled users or free preview lessons.
    """
    permission_classes = [AllowAny]

    def get(self, request, course_slug, lesson_id):
        course = get_object_or_404(Course, slug=course_slug, status='published')
        lesson = get_object_or_404(Lesson, lesson_id=lesson_id, section__course=course)

        # Check if user can access this lesson
        can_access = lesson.is_free_preview

        if request.user.is_authenticated:
            enrollment = Enrollment.objects.filter(
                student=request.user, course=course
            ).first()
            if enrollment:
                can_access = True
                # Update last accessed
                enrollment.last_accessed = timezone.now()
                enrollment.save(update_fields=['last_accessed'])

        if not can_access:
            return Response(
                {"message": "Enroll in this course to access this lesson"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = LessonSerializer(lesson)
        return Response(serializer.data)


class LessonProgressUpdateAPIView(APIView):
    """
    Update lesson progress (completion, time spent, video position).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, enrollment_id):
        enrollment = get_object_or_404(
            Enrollment, enrollment_id=enrollment_id, student=request.user
        )

        serializer = LessonProgressUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        lesson_id = serializer.validated_data['lesson_id']
        lesson = get_object_or_404(
            Lesson, lesson_id=lesson_id, section__course=enrollment.course
        )

        progress, created = LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson
        )

        # Update progress fields
        if 'is_completed' in serializer.validated_data:
            if serializer.validated_data['is_completed'] and not progress.is_completed:
                progress.is_completed = True
                progress.completed_at = timezone.now()
                enrollment.lessons_completed += 1

        if 'time_spent' in serializer.validated_data:
            progress.time_spent += serializer.validated_data['time_spent']

        if 'last_position' in serializer.validated_data:
            progress.last_position = serializer.validated_data['last_position']

        progress.save()

        # Update enrollment progress percentage
        total_lessons = enrollment.course.total_lessons
        if total_lessons > 0:
            enrollment.progress_percentage = int(
                (enrollment.lessons_completed / total_lessons) * 100
            )

            # Check if course completed
            if enrollment.progress_percentage >= 100:
                enrollment.status = 'completed'
                enrollment.completed_at = timezone.now()

        enrollment.last_accessed = timezone.now()
        enrollment.save()

        return Response({
            "message": "Progress updated",
            "progress_percentage": enrollment.progress_percentage,
            "lessons_completed": enrollment.lessons_completed
        })


# ============== Review Views ==============

class CourseReviewListAPIView(generics.ListAPIView):
    """
    List reviews for a course.
    """
    serializer_class = CourseReviewSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        course_slug = self.kwargs.get('course_slug')
        return CourseReview.objects.filter(
            course__slug=course_slug, is_approved=True
        ).select_related('student').order_by('-created_at')


class CourseReviewCreateAPIView(APIView):
    """
    Create or update a review for a course.
    User must be enrolled to review.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, course_slug):
        course = get_object_or_404(Course, slug=course_slug)

        # Check enrollment
        if not Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response(
                {"message": "You must be enrolled to review this course"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CourseReviewCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        review, created = CourseReview.objects.update_or_create(
            student=request.user,
            course=course,
            defaults={
                'rating': serializer.validated_data['rating'],
                'review_text': serializer.validated_data['review_text'],
                'is_approved': True  # Auto-approve for now
            }
        )

        # Update course rating
        avg_rating = CourseReview.objects.filter(
            course=course, is_approved=True
        ).aggregate(Avg('rating'))['rating__avg'] or 0

        course.average_rating = round(avg_rating, 2)
        course.total_reviews = CourseReview.objects.filter(course=course, is_approved=True).count()
        course.save(update_fields=['average_rating', 'total_reviews'])

        action = "created" if created else "updated"
        logger.info(f"Review {action} for course {course.title} by {request.user.email}")

        return Response(
            CourseReviewSerializer(review).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


# ============== Q&A Views ==============

class CourseQAListAPIView(generics.ListAPIView):
    """
    List Q&A for a course.
    """
    serializer_class = QuestionSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        course_slug = self.kwargs.get('course_slug')
        return Question.objects.filter(
            course__slug=course_slug
        ).select_related('student').prefetch_related('answers__user').order_by('-created_at')


class QuestionCreateAPIView(APIView):
    """
    Ask a question about a course or lesson.
    User must be enrolled.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, course_slug):
        course = get_object_or_404(Course, slug=course_slug)

        # Check enrollment
        if not Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response(
                {"message": "You must be enrolled to ask questions"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = QuestionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question = Question.objects.create(
            course=course,
            student=request.user,
            **serializer.validated_data
        )

        return Response(QuestionSerializer(question).data, status=status.HTTP_201_CREATED)


class AnswerCreateAPIView(APIView):
    """
    Answer a question.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, question_id):
        question = get_object_or_404(Question, question_id=question_id)

        serializer = AnswerCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        answer = Answer.objects.create(
            question=question,
            user=request.user,
            **serializer.validated_data
        )

        return Response(AnswerSerializer(answer).data, status=status.HTTP_201_CREATED)


# ============== Wishlist Views ==============

class WishlistListAPIView(generics.ListAPIView):
    """
    List user's wishlist.
    """
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(
            user=self.request.user
        ).select_related('course', 'course__instructor')


class WishlistToggleAPIView(APIView):
    """
    Add or remove a course from wishlist.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, course_id):
        course = get_object_or_404(Course, course_id=course_id, status='published')

        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            course=course
        )

        if not created:
            wishlist_item.delete()
            return Response({"message": "Removed from wishlist", "in_wishlist": False})

        return Response(
            {"message": "Added to wishlist", "in_wishlist": True},
            status=status.HTTP_201_CREATED
        )


class WishlistCheckAPIView(APIView):
    """
    Check if a course is in user's wishlist.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        in_wishlist = Wishlist.objects.filter(
            user=request.user, course__course_id=course_id
        ).exists()
        return Response({"in_wishlist": in_wishlist})


# ============== Notification Views ==============

class NotificationListAPIView(generics.ListAPIView):
    """
    List user's notifications.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        ).order_by('-created_at')[:50]


class NotificationMarkReadAPIView(APIView):
    """
    Mark notifications as read.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id=None):
        if notification_id:
            Notification.objects.filter(
                id=notification_id, user=request.user
            ).update(is_read=True)
        else:
            # Mark all as read
            Notification.objects.filter(user=request.user).update(is_read=True)

        return Response({"message": "Notifications marked as read"})


# ============== Instructor Views ==============

class InstructorDashboardAPIView(APIView):
    """
    Get instructor dashboard statistics.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        courses = Course.objects.filter(instructor=request.user)

        total_courses = courses.count()
        total_students = sum(c.total_students for c in courses)
        total_reviews = sum(c.total_reviews for c in courses)

        # Calculate earnings from completed orders
        total_earnings = OrderItem.objects.filter(
            instructor=request.user,
            order__status='completed'
        ).aggregate(total=Sum('price'))['total'] or 0

        return Response({
            "total_courses": total_courses,
            "total_students": total_students,
            "total_reviews": total_reviews,
            "total_earnings": float(total_earnings),
        })


class InstructorCoursesManageAPIView(generics.ListAPIView):
    """
    List instructor's own courses (all statuses).
    """
    serializer_class = CourseListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Course.objects.filter(
            instructor=self.request.user
        ).order_by('-created_at')


class InstructorCouponsAPIView(generics.ListAPIView):
    """
    List instructor's coupons.
    """
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Coupon.objects.filter(instructor=self.request.user)
