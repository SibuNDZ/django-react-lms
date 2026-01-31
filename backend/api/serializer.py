from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from userauths.models import Profile, User
from core.models import (
    Category, Course, Section, Lesson, LessonResource,
    Enrollment, LessonProgress, Cart, CartItem, Coupon,
    Order, OrderItem, CourseReview, Notification, Question, Answer, Wishlist
)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['full_name'] = user.full_name
        token['email'] = user.email
        token['username'] = user.username

        return token

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'password', 'password2']

    def validate(self, attr):
        if attr['password'] != attr['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attr
    
    def create(self, validated_data):
        user = User.objects.create(
            full_name=validated_data['full_name'],
            email=validated_data['email'],
        )

        email_username, _ = user.email.split("@")
        user.username = email_username
        user.set_password(validated_data['password'])
        user.save()

        return user

class UserSerializer(serializers.ModelSerializer):
    """Safe user serializer - excludes sensitive fields"""
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'full_name']  # Only safe fields


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed user serializer for authenticated user's own data"""
    class Meta:
        model = User
        exclude = ['password', 'otp', 'refresh_token']  # Exclude sensitive fields


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = "__all__"


# ============== Category Serializers ==============

class CategorySerializer(serializers.ModelSerializer):
    course_count = serializers.ReadOnlyField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'image', 'course_count']


# ============== Course Serializers ==============

class InstructorSerializer(serializers.ModelSerializer):
    """Simplified instructor info for course listings"""
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name']


class LessonResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonResource
        fields = ['id', 'resource_id', 'title', 'file', 'file_type', 'created_at']


class LessonSerializer(serializers.ModelSerializer):
    resources = LessonResourceSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = [
            'id', 'lesson_id', 'title', 'description', 'lesson_type',
            'content', 'video_url', 'video_file', 'duration', 'order',
            'is_free_preview', 'is_published', 'resources'
        ]


class LessonListSerializer(serializers.ModelSerializer):
    """Simplified lesson info for course curriculum (no video URLs for non-enrolled)"""
    class Meta:
        model = Lesson
        fields = [
            'id', 'lesson_id', 'title', 'description', 'lesson_type',
            'duration', 'order', 'is_free_preview', 'is_published'
        ]


class SectionSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = [
            'id', 'section_id', 'title', 'description', 'order',
            'total_lessons', 'total_duration', 'lessons'
        ]


class SectionListSerializer(serializers.ModelSerializer):
    """Section with limited lesson info for non-enrolled users"""
    lessons = LessonListSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = [
            'id', 'section_id', 'title', 'description', 'order',
            'total_lessons', 'total_duration', 'lessons'
        ]


class CourseListSerializer(serializers.ModelSerializer):
    """Simplified course info for listings"""
    instructor = InstructorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    discount_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Course
        fields = [
            'id', 'course_id', 'title', 'slug', 'short_description',
            'thumbnail', 'category', 'language', 'level', 'instructor',
            'price', 'original_price', 'is_free', 'discount_percentage',
            'total_sections', 'total_lessons', 'total_duration',
            'total_students', 'total_reviews', 'average_rating',
            'is_featured', 'created_at'
        ]


class CourseDetailSerializer(serializers.ModelSerializer):
    """Full course details for course page"""
    instructor = InstructorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    sections = SectionListSerializer(many=True, read_only=True)
    discount_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Course
        fields = [
            'id', 'course_id', 'title', 'slug', 'short_description', 'description',
            'thumbnail', 'intro_video', 'category', 'language', 'level', 'tags',
            'instructor', 'price', 'original_price', 'is_free', 'discount_percentage',
            'requirements', 'what_you_learn', 'target_audience', 'status',
            'total_sections', 'total_lessons', 'total_duration',
            'total_students', 'total_reviews', 'average_rating',
            'is_featured', 'published_at', 'created_at', 'updated_at', 'sections'
        ]


class CourseEnrolledSerializer(serializers.ModelSerializer):
    """Course details for enrolled students (includes full lesson content)"""
    instructor = InstructorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    sections = SectionSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'course_id', 'title', 'slug', 'short_description', 'description',
            'thumbnail', 'intro_video', 'category', 'language', 'level', 'tags',
            'instructor', 'price', 'original_price', 'is_free',
            'requirements', 'what_you_learn', 'target_audience',
            'total_sections', 'total_lessons', 'total_duration',
            'total_students', 'total_reviews', 'average_rating',
            'created_at', 'sections'
        ]


# ============== Cart Serializers ==============

class CartItemSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'course', 'price', 'added_at']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.ReadOnlyField()
    item_count = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = ['id', 'cart_id', 'items', 'total', 'item_count', 'created_at']


class CartItemCreateSerializer(serializers.Serializer):
    """Serializer for adding items to cart"""
    course_id = serializers.CharField()
    cart_id = serializers.CharField(required=False)


# ============== Order Serializers ==============

class OrderItemSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)
    instructor = InstructorSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'course', 'instructor', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    student = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'student', 'items', 'status',
            'subtotal', 'tax', 'discount', 'total', 'coupon',
            'payment_method', 'payment_id', 'created_at', 'completed_at'
        ]


class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating orders from cart"""
    cart_id = serializers.CharField()


class CouponApplySerializer(serializers.Serializer):
    """Serializer for applying coupons"""
    order_oid = serializers.CharField()
    coupon_code = serializers.CharField()


# ============== Enrollment Serializers ==============

class LessonProgressSerializer(serializers.ModelSerializer):
    lesson = LessonListSerializer(read_only=True)

    class Meta:
        model = LessonProgress
        fields = [
            'id', 'lesson', 'is_completed', 'completed_at',
            'time_spent', 'last_position', 'first_accessed', 'last_accessed'
        ]


class LessonProgressUpdateSerializer(serializers.Serializer):
    """Serializer for updating lesson progress"""
    lesson_id = serializers.CharField()
    is_completed = serializers.BooleanField(required=False, default=False)
    time_spent = serializers.IntegerField(required=False, default=0)
    last_position = serializers.IntegerField(required=False, default=0)


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)
    student = UserSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            'id', 'enrollment_id', 'student', 'course', 'status',
            'progress_percentage', 'lessons_completed', 'enrolled_at',
            'last_accessed', 'completed_at', 'certificate_issued', 'certificate_id'
        ]


class EnrollmentDetailSerializer(serializers.ModelSerializer):
    """Detailed enrollment with full course content and progress"""
    course = CourseEnrolledSerializer(read_only=True)
    lesson_progress = LessonProgressSerializer(many=True, read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            'id', 'enrollment_id', 'course', 'status',
            'progress_percentage', 'lessons_completed', 'enrolled_at',
            'last_accessed', 'completed_at', 'certificate_issued',
            'certificate_id', 'lesson_progress'
        ]


# ============== Review Serializers ==============

class CourseReviewSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)

    class Meta:
        model = CourseReview
        fields = [
            'id', 'review_id', 'student', 'rating', 'review_text',
            'helpful_count', 'created_at', 'updated_at'
        ]


class CourseReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseReview
        fields = ['rating', 'review_text']


# ============== Q&A Serializers ==============

class AnswerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Answer
        fields = ['id', 'answer_id', 'user', 'content', 'is_accepted', 'created_at']


class QuestionSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            'id', 'question_id', 'student', 'lesson', 'title',
            'content', 'is_resolved', 'answers', 'created_at'
        ]


class QuestionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['lesson', 'title', 'content']


class AnswerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['content']


# ============== Wishlist Serializers ==============

class WishlistSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'course', 'added_at']


# ============== Notification Serializers ==============

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'message',
            'is_read', 'course', 'order', 'created_at'
        ]


# ============== Coupon Serializers ==============

class CouponSerializer(serializers.ModelSerializer):
    is_valid = serializers.ReadOnlyField()

    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'discount_type', 'discount_value',
            'is_active', 'is_valid', 'valid_from', 'valid_until'
        ]
