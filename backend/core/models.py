from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import shortuuid


class Category(models.Model):
    """Course categories for organization"""
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(null=True, blank=True)
    icon = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to="category_images/", null=True, blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def course_count(self):
        return self.courses.filter(status='published').count()


class Course(models.Model):
    """Main course model - core of LMS"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
        ('zh', 'Chinese'),
        ('other', 'Other'),
    ]

    # Unique identifier
    course_id = models.CharField(max_length=20, unique=True, blank=True)

    # Basic Info
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    short_description = models.CharField(max_length=500, null=True, blank=True)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to="course_thumbnails/", null=True, blank=True)
    intro_video = models.URLField(null=True, blank=True)

    # Organization
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='courses'
    )
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default='en')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    tags = models.CharField(max_length=500, null=True, blank=True, help_text="Comma-separated tags")

    # Instructor/Creator
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses_created'
    )

    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_free = models.BooleanField(default=False)

    # Content Metadata
    requirements = models.TextField(null=True, blank=True, help_text="What students need to know before taking this course")
    what_you_learn = models.TextField(null=True, blank=True, help_text="What students will learn")
    target_audience = models.TextField(null=True, blank=True, help_text="Who this course is for")

    # Status & Publishing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)

    # Computed Metrics (updated by signals or tasks)
    total_sections = models.IntegerField(default=0)
    total_lessons = models.IntegerField(default=0)
    total_duration = models.IntegerField(default=0, help_text="Total duration in minutes")
    total_students = models.IntegerField(default=0)
    total_reviews = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['instructor']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.course_id:
            self.course_id = shortuuid.uuid()[:10].upper()
        if self.price == 0:
            self.is_free = True
        super().save(*args, **kwargs)

    @property
    def discount_percentage(self):
        if self.original_price and self.original_price > self.price:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0


class Section(models.Model):
    """Course sections - organize lessons"""
    section_id = models.CharField(max_length=20, unique=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    # Computed
    total_lessons = models.IntegerField(default=0)
    total_duration = models.IntegerField(default=0)  # minutes

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']
        unique_together = ('course', 'order')

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.section_id:
            self.section_id = shortuuid.uuid()[:10].upper()
        super().save(*args, **kwargs)


class Lesson(models.Model):
    """Individual lessons within sections"""
    LESSON_TYPE_CHOICES = [
        ('video', 'Video'),
        ('text', 'Text/Article'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
        ('resource', 'Resource'),
    ]

    lesson_id = models.CharField(max_length=20, unique=True, blank=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPE_CHOICES, default='video')

    # Content
    content = models.TextField(null=True, blank=True)  # For text lessons
    video_url = models.URLField(null=True, blank=True)  # For video lessons
    video_file = models.FileField(upload_to="lesson_videos/", null=True, blank=True)
    duration = models.IntegerField(default=0, help_text="Duration in minutes")

    # Metadata
    order = models.PositiveIntegerField(default=0)
    is_free_preview = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.section.title} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.lesson_id:
            self.lesson_id = shortuuid.uuid()[:10].upper()
        super().save(*args, **kwargs)


class LessonResource(models.Model):
    """Additional resources for lessons (PDFs, downloads, etc.)"""
    resource_id = models.CharField(max_length=20, unique=True, blank=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="lesson_resources/")
    file_type = models.CharField(max_length=50, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.resource_id:
            self.resource_id = shortuuid.uuid()[:10].upper()
        if self.file and not self.file_type:
            self.file_type = self.file.name.split('.')[-1].lower()
        super().save(*args, **kwargs)


class Enrollment(models.Model):
    """Student enrollment in courses"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
        ('expired', 'Expired'),
    ]

    enrollment_id = models.CharField(max_length=20, unique=True, blank=True)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # Progress Tracking
    progress_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    lessons_completed = models.IntegerField(default=0)

    # Timestamps
    enrolled_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Certificate
    certificate_issued = models.BooleanField(default=False)
    certificate_id = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        unique_together = ('student', 'course')
        ordering = ['-enrolled_at']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['course']),
        ]

    def __str__(self):
        return f"{self.student.email} - {self.course.title}"

    def save(self, *args, **kwargs):
        if not self.enrollment_id:
            self.enrollment_id = shortuuid.uuid()[:10].upper()
        super().save(*args, **kwargs)


class LessonProgress(models.Model):
    """Detailed tracking of individual lesson progress"""
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)

    # Completion
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Time tracking
    time_spent = models.IntegerField(default=0, help_text="Time spent in seconds")
    last_position = models.IntegerField(default=0, help_text="Video position in seconds for resume")

    # Timestamps
    first_accessed = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('enrollment', 'lesson')
        indexes = [
            models.Index(fields=['enrollment', 'is_completed']),
        ]

    def __str__(self):
        return f"{self.enrollment.student.email} - {self.lesson.title}"


class Cart(models.Model):
    """Shopping cart for course purchases"""
    cart_id = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carts'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.cart_id}"

    @property
    def total(self):
        return sum(item.price for item in self.items.all())

    @property
    def item_count(self):
        return self.items.count()


class CartItem(models.Model):
    """Individual items in cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'course')

    def __str__(self):
        return f"{self.cart.cart_id} - {self.course.title}"

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.course.price
        super().save(*args, **kwargs)


class Coupon(models.Model):
    """Discount coupons"""
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)

    # Restrictions
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='coupons',
        null=True,
        blank=True
    )
    courses = models.ManyToManyField(Course, blank=True, related_name='coupons')
    min_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_uses = models.IntegerField(default=0, help_text="0 = unlimited")
    times_used = models.IntegerField(default=0)

    # Validity
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

    @property
    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        if not self.is_active:
            return False
        if self.valid_from > now or self.valid_until < now:
            return False
        if self.max_uses > 0 and self.times_used >= self.max_uses:
            return False
        return True


class Order(models.Model):
    """Purchase orders for courses"""
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('free', 'Free'),
    ]

    # Order identifiers
    order_id = models.CharField(max_length=20, unique=True, blank=True)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )

    # Order Details
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')

    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    # Coupon
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)

    # Payment
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='stripe')
    payment_id = models.CharField(max_length=255, null=True, blank=True)
    stripe_payment_intent = models.CharField(max_length=255, null=True, blank=True)
    paypal_order_id = models.CharField(max_length=255, null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['order_id']),
            models.Index(fields=['payment_id']),
        ]

    def __str__(self):
        return f"Order {self.order_id} - {self.student.email}"

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = shortuuid.uuid()[:10].upper()
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """Individual courses in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='order_items'
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('order', 'course')

    def __str__(self):
        return f"{self.order.order_id} - {self.course.title}"


class CourseReview(models.Model):
    """Student reviews and ratings"""
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    review_id = models.CharField(max_length=20, unique=True, blank=True)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='course_reviews'
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')

    rating = models.IntegerField(choices=RATING_CHOICES)
    review_text = models.TextField()

    is_approved = models.BooleanField(default=True)
    helpful_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'course')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['course', 'rating']),
        ]

    def __str__(self):
        return f"{self.student.email} - {self.course.title} ({self.rating}*)"

    def save(self, *args, **kwargs):
        if not self.review_id:
            self.review_id = shortuuid.uuid()[:10].upper()
        super().save(*args, **kwargs)


class Notification(models.Model):
    """User notifications"""
    NOTIFICATION_TYPES = [
        ('enrollment', 'New Enrollment'),
        ('review', 'New Review'),
        ('order', 'Order Update'),
        ('course', 'Course Update'),
        ('system', 'System'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='system')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    # Optional reference to related objects
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.title}"


class Question(models.Model):
    """Q&A questions for courses"""
    question_id = models.CharField(max_length=20, unique=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='questions')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True)

    title = models.CharField(max_length=255)
    content = models.TextField()
    is_resolved = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.question_id:
            self.question_id = shortuuid.uuid()[:10].upper()
        super().save(*args, **kwargs)


class Answer(models.Model):
    """Answers to Q&A questions"""
    answer_id = models.CharField(max_length=20, unique=True, blank=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='answers'
    )

    content = models.TextField()
    is_accepted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_accepted', 'created_at']

    def __str__(self):
        return f"Answer to {self.question.title}"

    def save(self, *args, **kwargs):
        if not self.answer_id:
            self.answer_id = shortuuid.uuid()[:10].upper()
        super().save(*args, **kwargs)


class Wishlist(models.Model):
    """User wishlists for courses"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wishlists'
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='wishlisted_by')

    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.email} - {self.course.title}"


class CourseNote(models.Model):
    """Private study notes a student keeps against one of their enrollments"""
    note_id = models.CharField(max_length=20, unique=True, blank=True)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=255)
    note = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['enrollment', 'created_at']),
        ]

    def __str__(self):
        return f"{self.enrollment.student.email} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.note_id:
            self.note_id = shortuuid.uuid()[:10].upper()
        super().save(*args, **kwargs)


# ============== Assessment Models ==============

OUTCOME_CHOICES = [
    ('pending', 'Pending'),
    ('competent', 'Competent'),
    ('not_yet_competent', 'Not Yet Competent'),
]


class Quiz(models.Model):
    """An auto-marked quiz attached to a lesson of type 'quiz'"""
    quiz_id = models.CharField(max_length=20, unique=True, blank=True)
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='quiz')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    pass_mark = models.PositiveIntegerField(
        default=70, validators=[MaxValueValidator(100)],
        help_text="Percentage required to be marked competent"
    )
    max_attempts = models.PositiveIntegerField(default=0, help_text="0 = unlimited")
    time_limit_minutes = models.PositiveIntegerField(default=0, help_text="0 = no limit")
    shuffle_questions = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Quizzes'

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"

    @property
    def total_questions(self):
        return self.questions.count()

    @property
    def total_points(self):
        return sum(q.points for q in self.questions.all())

    def save(self, *args, **kwargs):
        if not self.quiz_id:
            self.quiz_id = shortuuid.uuid()[:10].upper()
        super().save(*args, **kwargs)


class QuizQuestion(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('single', 'Single correct answer'),
        ('multiple', 'Multiple correct answers'),
        ('true_false', 'True or false'),
    ]

    question_id = models.CharField(max_length=20, unique=True, blank=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='single')
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)
    explanation = models.TextField(blank=True, default='', help_text="Shown after the attempt is graded")

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.text[:80]

    def save(self, *args, **kwargs):
        if not self.question_id:
            self.question_id = shortuuid.uuid()[:10].upper()
        super().save(*args, **kwargs)


class QuizChoice(models.Model):
    choice_id = models.CharField(max_length=20, unique=True, blank=True)
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.text[:80]

    def save(self, *args, **kwargs):
        if not self.choice_id:
            self.choice_id = shortuuid.uuid()[:10].upper()
        super().save(*args, **kwargs)


class QuizAttempt(models.Model):
    """One sitting of a quiz by an enrolled student; graded server-side on submit"""
    STATUS_CHOICES = [
        ('in_progress', 'In progress'),
        ('submitted', 'Submitted'),
    ]

    attempt_id = models.CharField(max_length=20, unique=True, blank=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='quiz_attempts')
    attempt_number = models.PositiveIntegerField(default=1)

    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    # {question_id: {"selected": [choice_id, ...], "correct": bool, "points_awarded": int}}
    answers = models.JSONField(default=dict, blank=True)
    score = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    max_score = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES, default='pending')

    class Meta:
        unique_together = ('quiz', 'enrollment', 'attempt_number')
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['enrollment', 'quiz']),
        ]

    def __str__(self):
        return f"{self.enrollment.student.email} - {self.quiz.title} #{self.attempt_number}"

    @property
    def expires_at(self):
        if not self.quiz.time_limit_minutes or not self.started_at:
            return None
        from datetime import timedelta
        return self.started_at + timedelta(minutes=self.quiz.time_limit_minutes)

    @property
    def is_expired(self):
        expires_at = self.expires_at
        if expires_at is None or self.status != 'in_progress':
            return False
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() > expires_at + timedelta(seconds=30)

    def save(self, *args, **kwargs):
        if not self.attempt_id:
            self.attempt_id = shortuuid.uuid()[:10].upper()
        super().save(*args, **kwargs)


class Assignment(models.Model):
    """A practical task attached to a lesson of type 'assignment', graded by the instructor"""
    assignment_id = models.CharField(max_length=20, unique=True, blank=True)
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='assignment')
    title = models.CharField(max_length=255)
    instructions = models.TextField()
    max_score = models.PositiveIntegerField(default=100)
    pass_mark = models.PositiveIntegerField(
        default=50, validators=[MaxValueValidator(100)],
        help_text="Percentage of max_score required to be marked competent"
    )
    due_date = models.DateTimeField(null=True, blank=True)
    allow_resubmission = models.BooleanField(default=True)
    allowed_file_types = models.CharField(
        max_length=255, default='pdf,zip,ipynb,py,js,ts,csv,docx,md,txt',
        help_text="Comma-separated extensions; blank allows any"
    )
    max_file_size_mb = models.PositiveIntegerField(default=25)
    is_published = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"

    @property
    def allowed_extensions(self):
        return [ext.strip().lower().lstrip('.') for ext in self.allowed_file_types.split(',') if ext.strip()]

    def save(self, *args, **kwargs):
        if not self.assignment_id:
            self.assignment_id = shortuuid.uuid()[:10].upper()
        super().save(*args, **kwargs)


class AssignmentSubmission(models.Model):
    """A student's hand-in for an assignment, with the instructor's grading"""
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('graded', 'Graded'),
    ]

    submission_id = models.CharField(max_length=20, unique=True, blank=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='assignment_submissions')
    attempt_number = models.PositiveIntegerField(default=1)

    file = models.FileField(upload_to='assignment_submissions/%Y/%m/', null=True, blank=True)
    text_answer = models.TextField(blank=True, default='')
    link = models.URLField(blank=True, default='')
    submitted_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES, default='pending')
    score = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True, default='')
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='graded_submissions'
    )
    graded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('assignment', 'enrollment', 'attempt_number')
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['enrollment', 'assignment']),
            models.Index(fields=['assignment', 'status']),
        ]

    def __str__(self):
        return f"{self.enrollment.student.email} - {self.assignment.title} #{self.attempt_number}"

    @property
    def is_late(self):
        return bool(self.assignment.due_date and self.submitted_at and self.submitted_at > self.assignment.due_date)

    def save(self, *args, **kwargs):
        if not self.submission_id:
            self.submission_id = shortuuid.uuid()[:10].upper()
        super().save(*args, **kwargs)
