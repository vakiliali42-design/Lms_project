from django.db import models
from accounts.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    LEVEL_CHOICES = ("beginner","مبتدی"), ("intermidiate","متوسط"), ("advanced","پیشرقته")
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(max_length=500)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="taught_course")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    thumbnail = models.ImageField(upload_to="courses/thumbnails/", blank=True, null=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="beginner")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_published = models.BooleanField(default=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    students = models.ManyToManyField(User, through="enrollment", related_name="enrolled_course")

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        from django.utils import timezone
        today = timezone.now().date()

        if self.start_date and today < self.start_date:
            return False

        if self.end_date and today > self.end_date:
            return False

        return True

    def average_score(self):
        reviews = self.reviews.all()
        if reviews.exists():
            total = sum(review.score for review in reviews)
            return round(total / reviews.count(), 1)
        return 0


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=100)
    content = models.TextField()
    video_url = models.URLField(blank=True)
    file = models.FileField(upload_to="lessons/files/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("student", "course")

    def __str__(self):
        return f"{self.student} -> {self.course}"

class CourseContent(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="student_contents")
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    file = models.FileField(upload_to="student_uploads/")
    description = models.TextField(max_length=200)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.title}"


class Review(models.Model):
    SCORE_CHOICES = (
        (1, '★ خیلی بد'),
        (2, '★★ بد'),
        (3, '★★★ متوسط'),
        (4, '★★★★ خوب'),
        (5, '★★★★★ عالی'),
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    score = models.IntegerField(choices=SCORE_CHOICES)
    comment = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('course', 'student')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.username} -> {self.course.title} ({self.score}★)"