from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from .models import Course, Lesson, Enrollment, CourseContent, Review
from .forms import CourseForm, LessonForm, CourseContentForm, ReviewForm
from accounts.models import User
from notifications.utils import notify_enrollment
from django.views.decorators.cache import cache_page
from django.db.models import Q
from assignments.models import Assignment


def course_list(request):
    courses = Course.objects.filter(is_published=True)
    return render(request, 'courses/list.html', {'courses': courses})

def course_detail(request, slug):
    course   = get_object_or_404(Course, slug=slug)
    lessons  = course.lessons.all()
    reviews = course.reviews.select_related('student').all()
    enrolled = False
    user_review = None
    if request.user.is_authenticated:
        enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
        if enrolled:
            user_review = Review.objects.filter(student=request.user, course=course).first()
    return render(request, 'courses/detail.html', {
        'course': course, 'lessons': lessons, 'enrolled': enrolled, 'reviews': reviews, 'user_review': user_review,
    })

@login_required
def enroll_course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if request.user.is_student():
            enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course)
            if created:
                notify_enrollment(enrollment)
            messages.success(request, f'در دوره «{course.title}» ثبت‌نام شدید.')
    return redirect('course_detail', slug=slug)


@login_required
def create_course(request):
    if not request.user.is_teacher() and not request.user.is_admin():
        messages.error(request, 'دسترسی ندارید.')
        return redirect('course_list')
    form = CourseForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        course = form.save(commit=False)
        course.teacher = request.user
        course.slug    = slugify(course.title, allow_unicode=True)
        course.save()
        messages.success(request, 'دوره ساخته شد.')
        return redirect('course_detail', slug=course.slug)
    return render(request, 'courses/form.html', {'form': form, 'title': 'ایجاد دوره'})

@login_required
def edit_course(request, slug):
    course = get_object_or_404(Course, slug=slug)

    if request.user != course.teacher and not request.user.is_admin():
        messages.error(request, "دسترسی ندارید.")
        return redirect("course_detail", slug=slug)

    form = CourseForm(
        request.POST or None,
        request.FILES or None,
        instance=course,
    )

    if form.is_valid():
        form.save()
        messages.success(request, "دوره ویرایش شد.")
        return redirect("course_detail", slug=slug)

    return render(
        request,
        "courses/form.html",
        {
            "form": form,
            "title": "ویرایش دوره",
        },
    )


@login_required
def add_lesson(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if request.user != course.teacher and not request.user.is_admin():
        messages.error(request, 'دسترسی ندارید.')
        return redirect('course_detail', slug=slug)
    form = LessonForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        lesson = form.save(commit=False)
        lesson.course = course
        lesson.save()
        messages.success(request, 'جلسه اضافه شد.')
        return redirect('course_detail', slug=slug)
    return render(request, 'courses/form.html', {'form': form, 'title': 'افزودن جلسه'})

@login_required
def upload_content(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if not Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.error(request, 'ابتدا در دوره ثبت‌نام کنید.')
        return redirect('course_detail', slug=slug)
    form = CourseContentForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        content = form.save(commit=False)
        content.course  = course
        content.student = request.user
        content.save()
        messages.success(request, 'فایل آپلود شد.')
        return redirect('course_detail', slug=slug)
    return render(request, 'courses/form.html', {'form': form, 'title': 'آپلود محتوا'})

@login_required
def add_review(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if not Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.error(request, 'ابتدا در دوره ثبت‌نام کنید.')
        return redirect('course_detail', slug=slug)
    if Review.objects.filter(student=request.user, course=course).exists():
        messages.error(request, 'شما قبلاً نظر داده‌اید.')
        return redirect('course_detail', slug=slug)

    form = ReviewForm(request.POST or None)
    if form.is_valid():
        review = form.save(commit=False)
        review.course = course
        review.student = request.user
        review.save()
        messages.success(request, 'نظر شما ثبت شد.')
        return redirect('course_detail', slug=slug)
    return render(request, 'courses/form.html', {'form': form, 'course': course, 'title': 'ثبت نظر'})

@login_required
def remove_review(request, slug):
    course = get_object_or_404(Course, slug=slug)
    review = get_object_or_404(Review, course=course, student=request.user)

    if not (request.user == review.student or request.user.is_admin()):
        messages.error(request, 'دسترسی ندارید.')
        return redirect('course_detail', slug=slug)


    review.delete()
    messages.success(request, 'نظر شما حذف شد.')
    return redirect('course_detail', slug=slug)


@login_required
def course_students(request, slug):
    course = get_object_or_404(Course, slug=slug)

    # فقط استاد دوره یا ادمین
    if not (request.user == course.teacher or request.user.is_admin()):
        messages.error(request, 'دسترسی ندارید.')
        return redirect('course_detail', slug=slug)

    enrollments = Enrollment.objects.filter(
        course=course
    ).select_related('student')

    return render(request, 'courses/students.html', {
        'course':      course,
        'enrollments': enrollments,
    })

@login_required
def edit_lesson(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)

    if request.user != lesson.course.teacher and not request.user.is_admin():
        messages.error(request, "دسترسی ندارید.")
        return redirect("course_detail", slug=lesson.course.slug)

    form = LessonForm(
        request.POST or None,
        request.FILES or None,
        instance=lesson
    )

    if form.is_valid():
        form.save()
        messages.success(request, "جلسه ویرایش شد.")
        return redirect("course_detail", slug=lesson.course.slug)

    return render(request, "courses/form.html", {
        "form": form,
        "title": "ویرایش جلسه",
    })


@login_required
def delete_lesson(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)

    if request.user != lesson.course.teacher and not request.user.is_admin():
        messages.error(request, "دسترسی ندارید.")
        return redirect("course_detail", slug=lesson.course.slug)

    slug = lesson.course.slug
    lesson.delete()

    messages.success(request, "جلسه حذف شد.")
    return redirect("course_detail", slug=slug)


@login_required
def teacher_profile(request, pk):
    teacher = get_object_or_404(User, pk=pk, role="teacher")
    courses = Course.objects.filter(
        teacher=teacher,
        is_published=True
    ).order_by('created_at')
    return render(request, 'courses/teacher_profile.html', {
        'teacher':teacher,
        'courses':courses,
        'total_students':sum(c.students.count() for c in courses),
        'total_courses':courses.count()
    })

def global_search(request):
    q = request.GET.get('q', '').strip()

    results = {
        'courses':     [],
        'assignments': [],
        'teachers':    [],
        'query':        q,
    }

    if q:
        results['courses'] = Course.objects.filter(
            is_published=True
        ).filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(level__icontains=q)  |
            Q(price__icontains=q) |
            Q(teacher__first_name__icontains=q) |
            Q(teacher__last_name__icontains=q)
            ).select_related('teacher', 'category')[:10]

        results['assignments'] = Assignment.objects.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q)
        ).select_related('course', 'teacher')[:10]

        results["teachers"] = User.objects.filter(
            role = 'teacher').filter(
            Q(bio__icontains=q) |
            Q(email__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(username__icontains=q)
        )[:5]

        results['total'] = (
            len(results['courses']) +
            len(results['assignments']) +
            len(results['teachers'])
        )

    return render(request, 'courses/search.html', results)