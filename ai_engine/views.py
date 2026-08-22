# ai_engine/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .recommender import get_course_recommendations
from .plagiarism import check_plagiarism
from assignments.models import Assignment


@login_required
def recommendations_view(request):
    """
    صفحه پیشنهاد دوره برای دانشجو.
    فقط دانشجو میتونه ببینه.
    """
    if not request.user.is_student():
        messages.error(request, 'فقط دانشجو می‌تواند پیشنهادات را ببیند.')
        return redirect('dashboard')

    recommended = get_course_recommendations(request.user)

    return render(request, 'ai_engine/recommendations.html', {
        'recommended': recommended,
    })


@login_required
def plagiarism_check_view(request, assignment_pk):
    """
    بررسی تقلب برای یه تکلیف خاص.
    فقط استاد صاحب تکلیف یا ادمین میتونه ببینه.
    """
    assignment = get_object_or_404(Assignment, pk=assignment_pk)

    if not (request.user == assignment.teacher or request.user.is_admin()):
        messages.error(request, 'دسترسی ندارید.')
        return redirect('dashboard')

    # آستانه از GET parameter بگیر — پیش‌فرض ۷۰٪
    threshold = float(request.GET.get('threshold', 0.7))
    results   = check_plagiarism(assignment, threshold=threshold)

    return render(request, 'ai_engine/plagiarism.html', {
        'assignment': assignment,
        'results':    results,
        'threshold':  int(threshold * 100),
    })