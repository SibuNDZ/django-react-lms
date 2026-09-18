from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from django.conf import settings
from core.storage import build_presigned_url
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from userauths.models import Profile, User
from core.models import (
    Category, Course, Section, Lesson, LessonResource,
    Enrollment, LessonProgress, Cart, CartItem, Coupon,
    Order, OrderItem, CourseReview, Notification, Question, Answer, Wishlist,
    CourseNote
)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['full_name'] = user.full_name
        token['email'] = user.email
        token['username'] = user.username
        token['role'] = 'instructor' if user.is_instructor() else 'student'

        return token


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, required=False, default=User.ROLE_STUDENT)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'password', 'password2', 'role']

    def validate(self, attr):
        if attr['password'] != attr['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attr
    
    def create(self, validated_data):
        role = validated_data.pop('role', User.ROLE_STUDENT)
        if role not in (User.ROLE_STUDENT, User.ROLE_INSTRUCTOR):
            role = User.ROLE_STUDENT

        user = User.objects.create(
            full_name=validated_data['full_name'],
            email=validated_data['email'],
            role=role,
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
        fields = ['id', 'email', 'username', 'full_name', 'role']  # Only safe fields


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed user serializer for authenticated user's own data"""
    class Meta:
        model = User
        exclude = ['password', 'otp', 'refresh_token']  # Exclude sensitive fields


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'user', 'image', 'full_name', 'country', 'about', 'date']
        read_only_fields = ['id', 'user', 'date']


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
    file = serializers.SerializerMethodField()

    class Meta:
        model = LessonResource
        fields = ['id', 'resource_id', 'title', 'file', 'file_type', 'created_at']

    def get_file(self, obj):
        if not obj.file:
            return None
        if settings.USE_S3:
            return build_presigned_url(obj.file.name)
        request = self.context.get("request")
        return request.build_absolute_uri(obj.file.url) if request else obj.file.url


class LessonSerializer(serializers.ModelSerializer):
    resources = LessonResourceSerializer(many=True, read_only=True)
    video_file = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            'id', 'lesson_id', 'title', 'description', 'lesson_type',
            'content', 'video_url', 'video_file', 'duration', 'order',
            'is_free_preview', 'is_published', 'resources'
        ]

    def get_video_file(self, obj):
        if not obj.video_file:
            return None
        if settings.USE_S3:
            return build_presigned_url(obj.video_file.name)
        request = self.context.get("request")
        return request.build_absolute_uri(obj.video_file.url) if request else obj.video_file.url


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
            'status', 'total_sections', 'total_lessons', 'total_duration',
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
    oid = serializers.CharField(source='order_id', read_only=True)
    order_oid = serializers.CharField(source='order_id', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'oid', 'order_oid', 'student', 'items', 'status',
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


class CourseNoteSerializer(serializers.ModelSerializer):
    """A student's private note on an enrollment"""

    class Meta:
        model = CourseNote
        fields = ['id', 'note_id', 'title', 'note', 'created_at', 'updated_at']
        read_only_fields = ['id', 'note_id', 'created_at', 'updated_at']


class EnrollmentDetailSerializer(serializers.ModelSerializer):
    """Detailed enrollment with full course content, progress and notes"""
    course = CourseEnrolledSerializer(read_only=True)
    lesson_progress = LessonProgressSerializer(many=True, read_only=True)
    notes = CourseNoteSerializer(many=True, read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            'id', 'enrollment_id', 'course', 'status',
            'progress_percentage', 'lessons_completed', 'enrolled_at',
            'last_accessed', 'completed_at', 'certificate_issued',
            'certificate_id', 'lesson_progress', 'notes'
        ]


# ============== Review Serializers ==============

class CourseReviewSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    profile = serializers.SerializerMethodField()
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = CourseReview
        fields = [
            'id', 'review_id', 'student', 'profile', 'rating', 'review_text',
            'helpful_count', 'course', 'course_title', 'created_at', 'updated_at'
        ]

    def get_profile(self, obj):
        profile = getattr(obj.student, 'profile', None)
        return ProfileSerializer(profile, context=self.context).data if profile else None


class CourseReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseReview
        fields = ['rating', 'review_text']


# ============== Q&A Serializers ==============

class AnswerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    profile = serializers.SerializerMethodField()
    date = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Answer
        fields = [
            'id', 'answer_id', 'user', 'content', 'is_accepted',
            'profile', 'date', 'created_at'
        ]

    def get_profile(self, obj):
        profile = getattr(obj.user, 'profile', None)
        return ProfileSerializer(profile, context=self.context).data if profile else None


class QuestionSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)
    messages = AnswerSerializer(source='answers', many=True, read_only=True)
    profile = serializers.SerializerMethodField()
    date = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Question
        fields = [
            'id', 'question_id', 'student', 'lesson', 'title',
            'content', 'is_resolved', 'answers', 'messages', 'profile',
            'date', 'created_at', 'course'
        ]

    def get_profile(self, obj):
        profile = getattr(obj.student, 'profile', None)
        return ProfileSerializer(profile, context=self.context).data if profile else None


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
            'min_purchase', 'max_uses', 'times_used',
            'is_active', 'is_valid', 'valid_from', 'valid_until'
        ]
        read_only_fields = ['times_used']


class InstructorLessonWriteSerializer(serializers.Serializer):
    lesson_id = serializers.CharField(required=False, allow_blank=True)
    title = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True, default='')
    is_free_preview = serializers.BooleanField(required=False, default=False)
    duration = serializers.IntegerField(required=False, default=0)
    lesson_type = serializers.CharField(required=False, default='video')
    content = serializers.CharField(required=False, allow_blank=True, default='')
    video_url = serializers.CharField(required=False, allow_blank=True, default='')


class InstructorSectionWriteSerializer(serializers.Serializer):
    section_id = serializers.CharField(required=False, allow_blank=True)
    title = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True, default='')
    order = serializers.IntegerField(required=False, default=0)
    lessons = InstructorLessonWriteSerializer(many=True, required=False, default=list)


class InstructorCourseWriteSerializer(serializers.ModelSerializer):
    sections = InstructorSectionWriteSerializer(many=True, required=False, write_only=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Course
        fields = [
            'title', 'description', 'short_description', 'thumbnail', 'intro_video',
            'category', 'language', 'level', 'tags', 'price', 'original_price',
            'status', 'requirements', 'what_you_learn', 'target_audience', 'sections'
        ]

    def to_internal_value(self, data):
        if hasattr(data, 'lists'):
            data = {key: data.get(key) for key in data.keys()}
        elif hasattr(data, 'copy'):
            data = data.copy()
        sections = data.get('sections')
        if isinstance(sections, str):
            import json
            data['sections'] = json.loads(sections) if sections else []
        if data.get('image') and not data.get('thumbnail'):
            data['thumbnail'] = data.get('image')
        return super().to_internal_value(data)

    def create(self, validated_data):
        sections_data = validated_data.pop('sections', [])
        course = Course.objects.create(**validated_data)
        _sync_course_sections(course, sections_data)
        return course

    def update(self, instance, validated_data):
        sections_data = validated_data.pop('sections', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if sections_data is not None:
            _sync_course_sections(instance, sections_data)
        return instance


class InstructorCourseDetailSerializer(CourseDetailSerializer):
    """Full course payload for instructors, including unpublished lessons."""
    sections = SectionSerializer(many=True, read_only=True)
    category_id = serializers.SerializerMethodField()

    class Meta(CourseDetailSerializer.Meta):
        fields = list(CourseDetailSerializer.Meta.fields) + ['category_id']

    def get_category_id(self, obj):
        return obj.category_id


def _sync_course_sections(course, sections_data):
    from django.db.models import F

    Section.objects.filter(course=course).update(order=F('order') + 10000)

    kept_section_ids = []
    for index, section_data in enumerate(sections_data or []):
        section_id = section_data.get('section_id')
        lessons_data = section_data.get('lessons') or []
        defaults = {
            'title': section_data.get('title') or f'Section {index + 1}',
            'description': section_data.get('description') or '',
            'order': section_data.get('order', index),
        }
        if section_id:
            section = Section.objects.filter(course=course, section_id=section_id).first()
            if section:
                for attr, value in defaults.items():
                    setattr(section, attr, value)
                section.save()
            else:
                section = Section.objects.create(course=course, section_id=section_id, **defaults)
        else:
            section = Section.objects.create(course=course, **defaults)
        kept_section_ids.append(section.id)

        kept_lesson_ids = []
        for lesson_index, lesson_data in enumerate(lessons_data):
            lesson_id = lesson_data.get('lesson_id')
            lesson_defaults = {
                'title': lesson_data.get('title') or f'Lesson {lesson_index + 1}',
                'description': lesson_data.get('description') or '',
                'is_free_preview': lesson_data.get('is_free_preview', False),
                'duration': lesson_data.get('duration') or 0,
                'lesson_type': lesson_data.get('lesson_type') or 'video',
                'content': lesson_data.get('content') or '',
                'video_url': lesson_data.get('video_url') or None,
                'order': lesson_index,
            }
            if lesson_id:
                lesson = Lesson.objects.filter(section=section, lesson_id=lesson_id).first()
                if lesson:
                    for attr, value in lesson_defaults.items():
                        setattr(lesson, attr, value)
                    lesson.save()
                else:
                    lesson = Lesson.objects.create(section=section, lesson_id=lesson_id, **lesson_defaults)
            else:
                lesson = Lesson.objects.create(section=section, **lesson_defaults)
            kept_lesson_ids.append(lesson.id)
        Lesson.objects.filter(section=section).exclude(id__in=kept_lesson_ids).delete()

    Section.objects.filter(course=course).exclude(id__in=kept_section_ids).delete()
    course.total_sections = course.sections.count()
    course.total_lessons = sum(s.lessons.count() for s in course.sections.all())
    course.save(update_fields=['total_sections', 'total_lessons'])
