from django.contrib import admin
from .models import (
    Category, Course, Section, Lesson, LessonResource,
    Enrollment, LessonProgress, Cart, CartItem, Coupon,
    Order, OrderItem, CourseReview, Notification,
    Question, Answer, Wishlist
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'course_count', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']


class SectionInline(admin.TabularInline):
    model = Section
    extra = 0
    fields = ['title', 'order', 'total_lessons', 'total_duration']
    readonly_fields = ['total_lessons', 'total_duration']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'instructor', 'category', 'price', 'status',
        'total_students', 'average_rating', 'created_at'
    ]
    list_filter = ['status', 'category', 'level', 'language', 'is_free', 'is_featured']
    search_fields = ['title', 'description', 'instructor__email', 'course_id']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = [
        'course_id', 'total_sections', 'total_lessons', 'total_duration',
        'total_students', 'total_reviews', 'average_rating', 'created_at', 'updated_at'
    ]
    inlines = [SectionInline]
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Information', {
            'fields': ('course_id', 'title', 'slug', 'short_description', 'description', 'thumbnail', 'intro_video')
        }),
        ('Organization', {
            'fields': ('category', 'language', 'level', 'tags')
        }),
        ('Instructor', {
            'fields': ('instructor',)
        }),
        ('Pricing', {
            'fields': ('price', 'original_price', 'is_free')
        }),
        ('Content Details', {
            'fields': ('requirements', 'what_you_learn', 'target_audience')
        }),
        ('Status', {
            'fields': ('status', 'is_featured', 'published_at')
        }),
        ('Metrics (Auto-calculated)', {
            'fields': ('total_sections', 'total_lessons', 'total_duration', 'total_students', 'total_reviews', 'average_rating'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ['title', 'lesson_type', 'order', 'duration', 'is_free_preview', 'is_published']


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'total_lessons', 'total_duration']
    list_filter = ['course']
    search_fields = ['title', 'course__title']
    inlines = [LessonInline]
    readonly_fields = ['section_id', 'total_lessons', 'total_duration']


class LessonResourceInline(admin.TabularInline):
    model = LessonResource
    extra = 0


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'section', 'lesson_type', 'order', 'duration', 'is_free_preview', 'is_published']
    list_filter = ['lesson_type', 'is_free_preview', 'is_published', 'section__course']
    search_fields = ['title', 'section__title', 'section__course__title']
    inlines = [LessonResourceInline]
    readonly_fields = ['lesson_id']


@admin.register(LessonResource)
class LessonResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'file_type', 'created_at']
    list_filter = ['file_type']
    search_fields = ['title', 'lesson__title']
    readonly_fields = ['resource_id']


class LessonProgressInline(admin.TabularInline):
    model = LessonProgress
    extra = 0
    readonly_fields = ['lesson', 'is_completed', 'completed_at', 'time_spent']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = [
        'student', 'course', 'status', 'progress_percentage',
        'lessons_completed', 'enrolled_at', 'certificate_issued'
    ]
    list_filter = ['status', 'certificate_issued', 'enrolled_at']
    search_fields = ['student__email', 'course__title', 'enrollment_id']
    readonly_fields = ['enrollment_id', 'enrolled_at']
    inlines = [LessonProgressInline]
    date_hierarchy = 'enrolled_at'


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'lesson', 'is_completed', 'time_spent', 'last_accessed']
    list_filter = ['is_completed']
    search_fields = ['enrollment__student__email', 'lesson__title']


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['course', 'price', 'added_at']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['cart_id', 'user', 'item_count', 'total', 'created_at']
    search_fields = ['cart_id', 'user__email']
    inlines = [CartItemInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'course', 'price', 'added_at']
    search_fields = ['cart__cart_id', 'course__title']


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'discount_type', 'discount_value', 'instructor',
        'times_used', 'max_uses', 'is_active', 'valid_from', 'valid_until'
    ]
    list_filter = ['discount_type', 'is_active', 'instructor']
    search_fields = ['code', 'instructor__email']
    filter_horizontal = ['courses']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['course', 'instructor', 'price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_id', 'student', 'status', 'total', 'payment_method',
        'created_at', 'completed_at'
    ]
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order_id', 'student__email', 'payment_id']
    readonly_fields = [
        'order_id', 'subtotal', 'tax', 'discount', 'total',
        'payment_id', 'stripe_payment_intent', 'paypal_order_id',
        'created_at', 'updated_at'
    ]
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Order Info', {
            'fields': ('order_id', 'student', 'status')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'tax', 'discount', 'total', 'coupon')
        }),
        ('Payment', {
            'fields': ('payment_method', 'payment_id', 'stripe_payment_intent', 'paypal_order_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'course', 'instructor', 'price', 'created_at']
    search_fields = ['order__order_id', 'course__title']


@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'rating', 'is_approved', 'helpful_count', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['student__email', 'course__title', 'review_text']
    readonly_fields = ['review_id', 'created_at', 'updated_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__email', 'title', 'message']


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    fields = ['user', 'content', 'is_accepted', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'student', 'lesson', 'is_resolved', 'created_at']
    list_filter = ['is_resolved', 'course', 'created_at']
    search_fields = ['title', 'content', 'student__email', 'course__title']
    readonly_fields = ['question_id', 'created_at', 'updated_at']
    inlines = [AnswerInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['question', 'user', 'is_accepted', 'created_at']
    list_filter = ['is_accepted', 'created_at']
    search_fields = ['content', 'user__email', 'question__title']
    readonly_fields = ['answer_id', 'created_at', 'updated_at']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'added_at']
    search_fields = ['user__email', 'course__title']
    list_filter = ['added_at']
