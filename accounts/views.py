from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm, ProfileUpdateForm
from courses.models import Course, Lesson, Enrollment
from assignments.models import Assignment, Submission
from accounts.models import User

def register_view(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        if user.email:
            try:
                from notifications.tasks import send_welcome_email
                send_welcome_email.delay(
                    user_email=user.email,
                    user_name=user.get_full_name() or user.username,
                    role=user.get_role_display(),
                    site_url='http://120.0.0.8000'
                )
            except Exception:
                pass  # اگه Celery خطا داد، ثبت‌نام متوقف نشه

        messages.success(request, 'ثبت‌نام موفق!')
        return redirect('dashboard')

    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    form = LoginForm(request, data=request.POST or None)

    if form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect("home")

    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def profile_view(request):
    form = ProfileUpdateForm(request.POST or None, request.FILES or None, instance=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, "پروفایل آپدیت شد")
        return redirect("profile")
    return render(request, "accounts/profile.html", {"form":form})

@login_required
def dashboard_view(request):
    user = request.user
    ctx  = {}

    if user.is_student():
        # دوره‌های ثبت‌نامی دانشجو
        ctx['enrollments'] = Enrollment.objects.filter(
            student=user
        ).select_related('course').all()

        # تکالیف ارسال‌شده دانشجو
        ctx['submissions'] = Submission.objects.filter(
            student=user
        ).select_related('assignment__course').all()

    elif user.is_teacher():
        # دوره‌های استاد
        ctx['courses'] = Course.objects.filter(
            teacher=user
        ).all()

        # تکالیف تعریف‌شده استاد
        ctx['assignments'] = Assignment.objects.filter(
            teacher=user
        ).select_related('course').order_by('-created_at')[:10]

    elif user.is_admin():
        ctx['total_users']   = User.objects.count()
        ctx['total_courses'] = Course.objects.count()

    return render(request, 'accounts/dashboard.html', ctx)


def home_view(request):
    return render(request, 'home.html', {
        'total_courses':  Course.objects.filter(is_published=True).count(),
        'total_teachers': User.objects.filter(role='teacher').count(),
        'total_students': User.objects.filter(role='student').count(),
        'total_lessons':  Lesson.objects.count(),
        'recent_courses': Course.objects.filter(
            is_published=True
        ).order_by('-created_at')[:3],
    })