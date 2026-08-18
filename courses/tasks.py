from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Enrollment

@shared_task
def send_enrollment_email_task(enrollment_id):
    """
    ارسال غیرهمزمان ایمیل تایید ثبت‌نام در دوره
    """
    try:
        enrollment = Enrollment.objects.select_related('student', 'course').get(id=enrollment_id)
        subject = f"تایید ثبت‌نام در دوره {enrollment.course.title}"
        message = (
            f"سلام {enrollment.student.get_full_name() or enrollment.student.username} عزیز،\n\n"
            f"ثبت‌نام شما در دوره «{enrollment.course.title}» با موفقیت انجام شد.\n"
            f"مدرس دوره: {enrollment.course.teacher.get_full_name()}\n\n"
            f"با تشکر،\nسامانه مدیریت یادگیری"
        )
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[enrollment.student.email],
            fail_silently=False,
        )
    except Enrollment.DoesNotExist:
        pass