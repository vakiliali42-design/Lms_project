from rest_framework import serializers
from accounts.models import User
from courses.models import Course, Lesson, Enrollment, Category
from assignments.models import Assignment, Submission
from notifications.models import Notification


# ── User ──────────────────────────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    """
    نمایش اطلاعات کاربر.
    password فقط write_only هست — هیچوقت برگشت داده نمیشه.
    """
    class Meta:
        model  = User
        fields = ['id', 'username', 'first_name', 'last_name',
                  'email', 'role', 'bio', 'avatar']
        read_only_fields = ['id', 'role']


class RegisterSerializer(serializers.ModelSerializer):
    """سریالایزر ثبت‌نام — رمز دو بار گرفته میشه"""
    password2 = serializers.CharField(write_only=True)
    role      = serializers.ChoiceField(
        choices=['student', 'teacher']
    )

    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name',
                  'email', 'role', 'password', 'password2']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError('رمزها یکسان نیستند.')
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user     = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


# ── Category ──────────────────────────────────────────────

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Category
        fields = ['id', 'name', 'slug']


# ── Course ────────────────────────────────────────────────

class CourseListSerializer(serializers.ModelSerializer):
    """
    برای لیست دوره‌ها — اطلاعات کمتر، سریع‌تر.
    teacher_name فیلد محاسباتیه — از مدل نمیاد.
    """
    teacher_name    = serializers.SerializerMethodField()
    category_name   = serializers.SerializerMethodField()
    students_count  = serializers.SerializerMethodField()
    average_score   = serializers.SerializerMethodField()

    class Meta:
        model  = Course
        fields = ['id', 'title', 'slug', 'description',
                  'teacher_name', 'category_name',
                  'level', 'price', 'is_published',
                  'thumbnail', 'students_count',
                  'average_score', 'created_at']

    def get_teacher_name(self, obj):
        return obj.teacher.get_full_name() or obj.teacher.username

    def get_category_name(self, obj):
        return obj.category.name if obj.category else None

    def get_students_count(self, obj):
        return obj.students.count()

    def get_average_score(self, obj):
        return obj.average_score()


class CourseDetailSerializer(CourseListSerializer):
    """برای جزئیات دوره — شامل جلسات هم هست"""
    lessons = serializers.SerializerMethodField()

    class Meta(CourseListSerializer.Meta):
        fields = CourseListSerializer.Meta.fields + ['lessons']

    def get_lessons(self, obj):
        return LessonSerializer(
            obj.lessons.all(), many=True
        ).data


class CourseCreateSerializer(serializers.ModelSerializer):
    """برای ایجاد/ویرایش دوره توسط استاد"""
    class Meta:
        model  = Course
        fields = ['title', 'description', 'category',
                  'level', 'price', 'is_published', 'thumbnail']

    def create(self, validated_data):
        from django.utils.text import slugify
        validated_data['teacher'] = self.context['request'].user
        validated_data['slug']    = slugify(
            validated_data['title'], allow_unicode=True
        )
        return super().create(validated_data)


# ── Lesson ────────────────────────────────────────────────

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Lesson
        fields = ['id', 'title', 'content', 'video_url',
                  'file', 'order']
# ── Enrollment ────────────────────────────────────────────

class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(
        source='course.title', read_only=True
    )
    course_slug  = serializers.CharField(
        source='course.slug', read_only=True
    )

    class Meta:
        model  = Enrollment
        fields = ['id', 'course', 'course_title',
                  'course_slug', 'enrolled_at', 'completed']
        read_only_fields = ['id', 'enrolled_at']


# ── Assignment ────────────────────────────────────────────

class AssignmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(
        source='course.title', read_only=True
    )
    teacher_name = serializers.SerializerMethodField()

    class Meta:
        model  = Assignment
        fields = ['id', 'title', 'description', 'course',
                  'course_title', 'teacher_name',
                  'due_date', 'max_score', 'file', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_teacher_name(self, obj):
        return obj.teacher.get_full_name() or obj.teacher.username


# ── Submission ────────────────────────────────────────────

class SubmissionSerializer(serializers.ModelSerializer):
    student_name    = serializers.SerializerMethodField()
    assignment_title = serializers.CharField(
        source='assignment.title', read_only=True
    )

    class Meta:
        model  = Submission
        fields = ['id', 'assignment', 'assignment_title',
                  'student_name', 'file', 'note',
                  'score', 'feedback', 'status', 'submitted_at']
        read_only_fields = ['id', 'status', 'score',
                            'feedback', 'submitted_at']

    def get_student_name(self, obj):
        return obj.student.get_full_name() or obj.student.username


class GradeSerializer(serializers.ModelSerializer):
    """فقط برای نمره‌دهی استاد"""
    class Meta:
        model  = Submission
        fields = ['score', 'feedback']


# ── Notification ──────────────────────────────────────────

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Notification
        fields = ['id', 'notif_type', 'title', 'message',
                  'link', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']