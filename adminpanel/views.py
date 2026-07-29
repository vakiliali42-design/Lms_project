#adminpanel/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import User
from courses.models import Course, Enrollment
from assignments.models import Assignment, Submission
from notifications.models import Notification
from .forms import AdminUserForm, AdminCourseForm


# ── Mixin دسترسی ادمین ─────
def admin_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin():
            messages.error(request, 'فقط ادمین دسترسی دارد.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


# ── داشبورد ادمین ─────
@login_required
@admin_required
def admin_dashboard(request):
    ctx = {
        'total_users':       User.objects.count(),
        'total_students':    User.objects.filter(role='student').count(),
        'total_teachers':    User.objects.filter(role='teacher').count(),
        'total_courses':     Course.objects.count(),
        'published_courses': Course.objects.filter(is_published=True).count(),
        'total_assignments': Assignment.objects.count(),
        'total_submissions': Submission.objects.count(),
        'graded':            Submission.objects.filter(status='graded').count(),
        'pending':           Submission.objects.filter(status='submitted').count(),
        'late':              Submission.objects.filter(status='late').count(),
        'total_notifs':      Notification.objects.count(),
        'unread_notifs':     Notification.objects.filter(is_read=False).count(),
        'recent_users':      User.objects.order_by('-date_joined')[:5],
        'recent_courses':    Course.objects.order_by('-created_at')[:5],
    }
    return render(request, 'adminpanel/dashboard.html', ctx)


# ══════════════════════════════════════════════════════════
# مدیریت کاربران
# ══════════════════════════════════════════════════════════

@login_required
@admin_required
def user_list(request):
    users = User.objects.all().order_by('-date_joined')

    # فیلتر
    role = request.GET.get('role')
    q    = request.GET.get('q')
    if role:
        users = users.filter(role=role)
    if q:
        users = users.filter(username__icontains=q) | \
                users.filter(email__icontains=q)    | \
                users.filter(first_name__icontains=q)

    return render(request, 'adminpanel/user_list.html', {
        'users':       users,
        'total':       users.count(),
        'role_filter': role,
        'q':           q,
    })


@login_required
@admin_required
def user_create(request):
    form = AdminUserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        messages.success(request, f'کاربر {user.username} ایجاد شد.')
        return redirect('admin_user_list')
    return render(request, 'adminpanel/user_form.html', {
        'form': form, 'title': 'ایجاد کاربر'
    })


@login_required
@admin_required
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = AdminUserForm(request.POST or None, instance=user)
    if form.is_valid():
        user = form.save(commit=False)
        if form.cleaned_data.get('password'):
            user.set_password(form.cleaned_data['password'])
        user.save()
        messages.success(request, 'اطلاعات کاربر ویرایش شد.')
        return redirect('admin_user_list')
    return render(request, 'adminpanel/user_form.html', {
        'form': form, 'title': 'ویرایش کاربر', 'user_obj': user
    })
@login_required
@admin_required
def user_toggle_active(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, 'نمی‌توانید حساب خودتان را غیرفعال کنید.')
        return redirect('admin_user_list')
    user.is_active = not user.is_active
    user.save()
    status = 'فعال' if user.is_active else 'غیرفعال'
    messages.success(request, f'حساب {user.username} {status} شد.')
    return redirect('admin_user_list')


@login_required
@admin_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, 'نمی‌توانید حساب خودتان را حذف کنید.')
        return redirect('admin_user_list')
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'کاربر {username} حذف شد.')
        return redirect('admin_user_list')
    return render(request, 'adminpanel/confirm_delete.html', {
        'obj': user, 'title': 'حذف کاربر'
    })


# ══════════════════════════════════════════════════════════
# مدیریت دوره‌ها
# ══════════════════════════════════════════════════════════

@login_required
@admin_required
def course_list_admin(request):
    courses = Course.objects.select_related(
        'teacher', 'category'
    ).order_by('-created_at')

    q = request.GET.get('q')
    published = request.GET.get('published')
    if q:
        courses = courses.filter(title__icontains=q)
    if published == '1':
        courses = courses.filter(is_published=True)
    elif published == '0':
        courses = courses.filter(is_published=False)

    return render(request, 'adminpanel/course_list.html', {
        'courses': courses,
        'total':   courses.count(),
    })


@login_required
@admin_required
def course_toggle_publish(request, pk):
    course = get_object_or_404(Course, pk=pk)
    course.is_published = not course.is_published
    course.save()
    status = 'منتشر' if course.is_published else 'پیش‌نویس'
    messages.success(request, f'دوره «{course.title}» {status} شد.')
    return redirect('admin_course_list')


@login_required
@admin_required
def course_edit_admin(request, pk):
    course = get_object_or_404(Course, pk=pk)
    form   = AdminCourseForm(request.POST or None,
                             request.FILES or None,
                             instance=course)
    if form.is_valid():
        form.save()
        messages.success(request, 'دوره ویرایش شد.')
        return redirect('admin_course_list')
    return render(request, 'adminpanel/course_form.html', {
        'form': form, 'course': course
    })


@login_required
@admin_required
def course_delete_admin(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        title = course.title
        course.delete()
        messages.success(request, f'دوره «{title}» حذف شد.')
        return redirect('admin_course_list')
    return render(request, 'adminpanel/confirm_delete.html', {
        'obj': course, 'title': 'حذف دوره'
    })


# ══════════════════════════════════════════════════════════
# مدیریت تکالیف و نمرات
# ══════════════════════════════════════════════════════════

@login_required
@admin_required
def assignment_list_admin(request):
    assignments = Assignment.objects.select_related(
        'course', 'teacher'
    ).order_by('-created_at')
    return render(request, 'adminpanel/assignment_list.html', {
        'assignments': assignments,
    })


@login_required
@admin_required
def submission_list_admin(request, assignment_pk):
    assignment  = get_object_or_404(Assignment, pk=assignment_pk)
    submissions = assignment.submissions.select_related('student').all()
    return render(request, 'adminpanel/submission_list.html', {
        'assignment':  assignment,
        'submissions': submissions,
    })
@login_required
@admin_required
def submission_delete_admin(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    assignment_pk = submission.assignment.pk
    if request.method == 'POST':
        submission.delete()
        messages.success(request, 'ارسال حذف شد.')
        return redirect('admin_submission_list', assignment_pk=assignment_pk)
    return render(request, 'adminpanel/confirm_delete.html', {
        'obj': submission, 'title': 'حذف ارسال'
    })