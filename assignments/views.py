from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Assignment, Submission
from .forms import AssignmentForm, SubmissionForm, GradeForm
from courses.models import Course, Enrollment
from notifications.utils import (
    notify_new_assignment,
    notify_submission_received,
    notify_grade_given
)


# ── Assignment Views ──────────────────────────────────────

@login_required
def assignment_list(request, course_slug):
    course      = get_object_or_404(Course, slug=course_slug)
    assignments = Assignment.objects.filter(
        course=course
    ).order_by('due_date')

    # تکالیف ارسال‌شده دانشجو
    my_submissions = {}
    if request.user.is_student():
        my_submissions = {
            s.assignment_id: s
            for s in Submission.objects.filter(
                student=request.user,
                assignment__course=course
            )
        }

    return render(request, 'assignments/list.html', {
        'course':         course,
        'assignments':    assignments,
        'my_submissions': my_submissions,
    })


@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    ctx = {'assignment': assignment}

    if request.user.is_student():
        ctx['my_submission'] = Submission.objects.filter(
            assignment=assignment,
            student=request.user
        ).first()

    elif request.user.is_teacher() or request.user.is_admin():
        ctx['submissions'] = assignment.submissions.select_related('student').all()

    return render(request, 'assignments/detail.html', ctx)


@login_required
def create_assignment(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)

    # کنترل دسترسی
    if not (request.user == course.teacher or request.user.is_admin()):
        messages.error(request, 'دسترسی ندارید.')
        return redirect('assignment_list', course_slug=course_slug)

    form = AssignmentForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        assignment         = form.save(commit=False)
        assignment.course  = course
        assignment.teacher = request.user
        assignment.save()

        # ← اعلان به همه دانشجویان دوره
        notify_new_assignment(assignment)

        messages.success(request, 'تکلیف ایجاد شد.')
        return redirect('assignment_list', course_slug=course.slug)

    return render(request, 'assignments/form.html', {
        'form':  form,
        'title': 'ایجاد تکلیف',
    })


@login_required
def edit_assignment(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)

    # کنترل دسترسی
    if not (request.user == assignment.teacher or request.user.is_admin()):
        messages.error(request, 'دسترسی ندارید.')
        return redirect('assignment_list',
                        course_slug=assignment.course.slug)

    form = AssignmentForm(
        request.POST or None,
        request.FILES or None,
        instance=assignment
    )
    if form.is_valid():
        form.save()
        messages.success(request, 'تکلیف ویرایش شد.')
        return redirect('assignment_list',
                        course_slug=assignment.course.slug)

    return render(request, 'assignments/form.html', {
        'form':  form,
        'title': 'ویرایش تکلیف',
    })


# ── Submission Views ──────────────────────────────────────

@login_required
def submit_assignment(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)

    # کنترل دسترسی — فقط دانشجوی ثبت‌نامی
    if not Enrollment.objects.filter(
        student=request.user,
        course=assignment.course
    ).exists():
        messages.error(request, 'ابتدا در دوره ثبت‌نام کنید.')
        return redirect('course_list')

    if Submission.objects.filter(
        assignment=assignment,
        student=request.user
    ).exists():
        messages.warning(request, 'قبلاً ارسال کرده‌اید.')
        return redirect('assignment_list',
                        course_slug=assignment.course.slug)

    form = SubmissionForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        submission            = form.save(commit=False)
        submission.assignment = assignment
        submission.student    = request.user
        submission.status     = (
            'late' if timezone.now() > assignment.due_date
            else 'submitted'
        )
        submission.save()

        # ← اعلان به استاد
        notify_submission_received(submission)

        messages.success(request, 'تکلیف ارسال شد.')
        return redirect('assignment_list',
                        course_slug=assignment.course.slug)

    return render(request, 'assignments/form.html', {
        'form':       form,
        'title':      'ارسال تکلیف',
        'assignment': assignment,
    })


@login_required
def grade_submission(request, pk):
    submission = get_object_or_404(Submission, pk=pk)

    # کنترل دسترسی
    if not (request.user == submission.assignment.teacher
            or request.user.is_admin()):
        messages.error(request, 'دسترسی ندارید.')
        return redirect('course_list')

    form = GradeForm(request.POST or None, instance=submission)
    if form.is_valid():
        s        = form.save(commit=False)
        s.status = 'graded'
        s.save()

        # ← اعلان به دانشجو
        notify_grade_given(s)

        messages.success(request, 'نمره ثبت شد.')
        return redirect('assignment_list',
                        course_slug=submission.assignment.course.slug)

    return render(request, 'assignments/form.html', {
        'form':       form,
        'title':      'نمره‌دهی',
        'submission': submission,
    })