from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone

from accounts.models import User
from courses.models import Course, Lesson, Enrollment
from assignments.models import Assignment, Submission
from notifications.models import Notification

from .serializers import (
    UserSerializer, RegisterSerializer,
    CourseListSerializer, CourseDetailSerializer, CourseCreateSerializer,
    LessonSerializer, EnrollmentSerializer,
    AssignmentSerializer, SubmissionSerializer, GradeSerializer,
    NotificationSerializer,
)
from .permissions import (
    IsStudent, IsTeacher, IsTeacherOrAdmin, IsCourseOwner
)


# ══════════════════════════════════════════════════════════
# Auth
# ══════════════════════════════════════════════════════════

class RegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/
    ثبت‌نام کاربر جدید — نیازی به احراز هویت نداره.
    """
    serializer_class   = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # ارسال ایمیل خوش‌آمد
        if user.email:
            try:
                from notifications.tasks import send_welcome_email
                send_welcome_email.delay(
                    user_email = user.email,
                    user_name  = user.get_full_name() or user.username,
                    role       = user.get_role_display(),
                    site_url   = 'http://127.0.0.1:8000',
                )
            except Exception:
                pass

        return Response(
            {'message': 'ثبت‌نام موفق!',
             'user': UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    GET  /api/auth/profile/ → مشاهده پروفایل
    PUT  /api/auth/profile/ → ویرایش پروفایل
    """
    serializer_class   = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# ══════════════════════════════════════════════════════════
# Courses
# ══════════════════════════════════════════════════════════

class CourseListView(generics.ListAPIView):
    """
    GET /api/courses/ → لیست دوره‌های منتشرشده
    فیلتر: ?level=beginner&q=python
    """
    serializer_class   = CourseListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs    = Course.objects.filter(
            is_published=True
        ).select_related('teacher', 'category')
        level = self.request.query_params.get('level')
        q     = self.request.query_params.get('q')
        if level:
            qs = qs.filter(level=level)
        if q:
            qs = qs.filter(title__icontains=q)
        return qs


class CourseDetailView(generics.RetrieveAPIView):
    """GET /api/courses/<slug>/"""
    serializer_class   = CourseDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field       = 'slug'
    queryset           = Course.objects.filter(is_published=True)


class CourseCreateView(generics.CreateAPIView):
    """POST /api/courses/create/ — فقط استاد"""
    serializer_class   = CourseCreateSerializer
    permission_classes = [IsTeacherOrAdmin]


class CourseUpdateView(generics.UpdateAPIView):
    """PUT /api/courses/<slug>/edit/ — فقط صاحب دوره"""
    serializer_class   = CourseCreateSerializer
    permission_classes = [IsTeacherOrAdmin, IsCourseOwner]
    lookup_field       = 'slug'
    queryset           = Course.objects.all()


class EnrollView(APIView):
    """
    POST /api/courses/<slug>/enroll/
    دانشجو در دوره ثبت‌نام می‌کنه.
    """
    permission_classes = [IsStudent]
    def post(self, request, slug):
        course = get_object_or_404(Course, slug=slug, is_published=True)
        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user, course=course
        )
        if created:
            from notifications.utils import notify_enrollment
            notify_enrollment(enrollment)
            return Response(
                {'message': f'در دوره «{course.title}» ثبت‌نام شدید.'},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {'message': 'قبلاً ثبت‌نام کرده‌اید.'},
            status=status.HTTP_200_OK,
        )


class MyCoursesView(generics.ListAPIView):
    """GET /api/courses/my/ — دوره‌های ثبت‌نام‌شده دانشجو"""
    serializer_class   = EnrollmentSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        return Enrollment.objects.filter(
            student=self.request.user
        ).select_related('course')


class TeacherCoursesView(generics.ListAPIView):
    """GET /api/courses/teaching/ — دوره‌های استاد"""
    serializer_class   = CourseListSerializer
    permission_classes = [IsTeacherOrAdmin]

    def get_queryset(self):
        return Course.objects.filter(
            teacher=self.request.user
        )


# ══════════════════════════════════════════════════════════
# Assignments
# ══════════════════════════════════════════════════════════

class AssignmentListView(generics.ListAPIView):
    """GET /api/assignments/?course=<slug>"""
    serializer_class   = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        course_slug = self.request.query_params.get('course')
        qs          = Assignment.objects.select_related('course', 'teacher')
        if course_slug:
            qs = qs.filter(course__slug=course_slug)
        return qs


class AssignmentCreateView(generics.CreateAPIView):
    """POST /api/assignments/create/"""
    serializer_class   = AssignmentSerializer
    permission_classes = [IsTeacherOrAdmin]

    def perform_create(self, serializer):
        assignment = serializer.save(teacher=self.request.user)
        from notifications.utils import notify_new_assignment
        notify_new_assignment(assignment)


class SubmitAssignmentView(APIView):
    """POST /api/assignments/<pk>/submit/"""
    permission_classes = [IsStudent]

    def post(self, request, pk):
        assignment = get_object_or_404(Assignment, pk=pk)

        # چک ثبت‌نام
        if not Enrollment.objects.filter(
            student=request.user, course=assignment.course
        ).exists():
            return Response(
                {'error': 'ابتدا در دوره ثبت‌نام کنید.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        # چک ارسال قبلی
        if Submission.objects.filter(
            assignment=assignment, student=request.user
        ).exists():
            return Response(
                {'error': 'قبلاً ارسال کرده‌اید.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = SubmissionSerializer(data=request.data)
        if serializer.is_valid():
            submission = serializer.save(
                assignment = assignment,
                student    = request.user,
                status     = (
                    'late' if timezone.now() > assignment.due_date
                    else 'submitted'
                ),
            )
            from notifications.utils import notify_submission_received
            notify_submission_received(submission)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class GradeSubmissionView(generics.UpdateAPIView):
    """PATCH /api/assignments/submission/<pk>/grade/"""
    serializer_class   = GradeSerializer
    permission_classes = [IsTeacherOrAdmin]
    queryset           = Submission.objects.all()
    def perform_update(self, serializer):
        submission        = serializer.save(status='graded')
        from notifications.utils import notify_grade_given
        notify_grade_given(submission)


class SubmissionListView(generics.ListAPIView):
    """GET /api/assignments/<pk>/submissions/ — برای استاد"""
    serializer_class   = SubmissionSerializer
    permission_classes = [IsTeacherOrAdmin]

    def get_queryset(self):
        assignment = get_object_or_404(
            Assignment, pk=self.kwargs['pk']
        )
        return assignment.submissions.select_related('student')


# ══════════════════════════════════════════════════════════
# Notifications
# ══════════════════════════════════════════════════════════

class NotificationListView(generics.ListAPIView):
    """GET /api/notifications/"""
    serializer_class   = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).order_by('-created_at')


class MarkReadView(APIView):
    """POST /api/notifications/<pk>/read/"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        notif = get_object_or_404(
            Notification, pk=pk, recipient=request.user
        )
        notif.is_read = True
        notif.save()
        return Response({'message': 'خوانده شد.'})


class MarkAllReadView(APIView):
    """POST /api/notifications/read-all/"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        count = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).update(is_read=True)
        return Response({'message': f'{count} اعلان خوانده شد.'})
