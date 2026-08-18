import logging
from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

logger   = logging.getLogger(__name__)
SITE_URL = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')


# ══════════════════════════════════════════════════════════
# تابع کمکی — ارسال HTML Email
# ══════════════════════════════════════════════════════════

def _send_html_email(subject, template_name, context, recipient_email):
    """
    ارسال ایمیل HTML با EmailMultiAlternatives.
    هم نسخه HTML هم نسخه متنی دارد —
    کلاینت‌هایی که HTML نمی‌خونن متن ساده می‌بینن.
    """
    html_content = render_to_string(template_name, context)
    text_content = 'لطفاً این ایمیل را با یک کلاینت HTML مشاهده کنید.'

    msg = EmailMultiAlternatives(
        subject    = subject,
        body       = text_content,
        from_email = settings.DEFAULT_FROM_EMAIL,
        to         = [recipient_email],
    )
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


# ══════════════════════════════════════════════════════════
# Exponential Backoff — تابع کمکی برای محاسبه تاخیر retry
# ══════════════════════════════════════════════════════════

def _get_retry_countdown(retries):
    """
    Exponential Backoff:
    هر بار که retry می‌کنه، تاخیر دو برابر میشه.

    retry 1: 60  ثانیه صبر کن (۱ دقیقه)
    retry 2: 120 ثانیه صبر کن (۲ دقیقه)
    retry 3: 240 ثانیه صبر کن (۴ دقیقه)

    چرا؟ اگه Gmail موقتاً قطعه، یه دقیقه بعد
    احتمال زیاده که برگشته باشه. اگه هنوز نه،
    دو دقیقه بعد. اینطوری سرور رو spam نمی‌کنیم.
    """
    return 60 * (2 ** retries)


# ══════════════════════════════════════════════════════════
# خطاهایی که retry ندارن (خطای دائمی)
# ══════════════════════════════════════════════════════════

PERMANENT_ERRORS = (
    # ایمیل نامعتبر — retry فایده نداره
    'invalid recipient',
    'user unknown',
    'does not exist',
    'no such user',
    # دامنه نامعتبر
    'domain not found',
    'name or service not known',
)


def _is_permanent_error(error_msg):
    """
    چک می‌کنه خطا دائمیه یا موقت.
    خطای دائمی = ایمیل اشتباهه، retry فایده نداره.
    خطای موقت = شبکه کنده، Gmail قطعه، retry فایده داره.
    """
    error_lower = error_msg.lower()
    return any(err in error_lower for err in PERMANENT_ERRORS)


# ══════════════════════════════════════════════════════════
# تسک پایه — ارسال ایمیل ساده
# ══════════════════════════════════════════════════════════

@shared_task(
    bind              = True,
    max_retries       = 3,
    # retry_backoff: هر retry دیرتر اجرا میشه
    retry_backoff     = True,
    # وقتی تسک رو دریافت کرد، تایم‌اوت ۳۰ ثانیه
    soft_time_limit   = 30,
    # اگه بیشتر از ۶۰ ثانیه طول کشید، kill بشه
    time_limit        = 60,
)
def send_email_task(self, recipient_email, subject, message):
    """
    ارسال ایمیل متنی ساده با Retry حرفه‌ای.

    جریان:
    1. سعی می‌کنه ایمیل بفرسته
    2. اگه خطای دائمی → لاگ می‌کنه و retry نمی‌کنه
    3. اگه خطای موقت → با Exponential Backoff retry می‌کنه
    4. اگه بعد از ۳ retry هنوز خطا → لاگ می‌کنه
    """
    try:
        from django.core.mail import send_mail
        send_mail(
            subject        = subject,
            message        = message,
            from_email     = settings.DEFAULT_FROM_EMAIL,
            recipient_list = [recipient_email],
            fail_silently  = False,
        )
        logger.info(f'✅ ایمیل به {recipient_email} ارسال شد')
        return f'success:{recipient_email}'

    except Exception as exc:
        error_msg = str(exc)
        logger.error(f'❌ خطا در ارسال ایمیل به {recipient_email}: {error_msg}')

        # خطای دائمی — retry نکن
        if _is_permanent_error(error_msg):
            logger.error(f'🚫 خطای دائمی — retry نمی‌شه: {error_msg}')
            return f'permanent_error:{recipient_email}'
# خطای موقت — با Backoff retry کن
        try:
            countdown = _get_retry_countdown(self.request.retries)
            logger.warning(
                f'retry {self.request.retries + 1}/3 '
                f'بعد از {countdown} ثانیه برای {recipient_email}'
            )
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            logger.critical(
                f' بعد از ۳ بار retry هم نشد ایمیل به {recipient_email} بره'
            )
            return f'max_retries_exceeded:{recipient_email}'


# ══════════════════════════════════════════════════════════
# تسک‌های HTML Email با Retry حرفه‌ای
# ══════════════════════════════════════════════════════════

@shared_task(
    bind            = True,
    max_retries     = 3,
    soft_time_limit = 30,
    time_limit      = 60,
)
def send_assignment_email(self, student_email, student_name,
                          course_title, assignment_title,
                          due_date, max_score, description,
                          assignment_pk, teacher_name):
    """
    ایمیل HTML برای تکلیف جدید.
    اگه template پیدا نشد → خطای دائمیه، retry نکن.
    اگه Gmail قطعه → retry با Backoff.
    """
    try:
        _send_html_email(
            subject       = f'📋 تکلیف جدید: {assignment_title}',
            template_name = 'emails/assignment_email.html',
            context       = {
                'student_name':     student_name,
                'teacher_name':     teacher_name,
                'course_title':     course_title,
                'assignment_title': assignment_title,
                'due_date':         due_date,
                'max_score':        max_score,
                'description':      description,
                'assignment_pk':    assignment_pk,
                'site_url':         SITE_URL,
            },
            recipient_email = student_email,
        )
        logger.info(f'✅ ایمیل تکلیف به {student_email} ارسال شد')
        return f'success:{student_email}'

    except Exception as exc:
        error_msg = str(exc)
        logger.error(f'❌ خطا در ایمیل تکلیف به {student_email}: {error_msg}')

        if _is_permanent_error(error_msg):
            return f'permanent_error:{student_email}'

        try:
            countdown = _get_retry_countdown(self.request.retries)
            raise self.retry(exc=exc, countdown=countdown)
        except MaxRetriesExceededError:
            logger.critical(f'ایمیل تکلیف به {student_email} شکست')
            return f'max_retries_exceeded:{student_email}'


@shared_task(
    bind            = True,
    max_retries     = 3,
    soft_time_limit = 30,
    time_limit      = 60,
)
def send_grade_email(self, student_email, student_name,
                     assignment_title, course_title,
                     score, max_score, feedback,
                     assignment_pk, teacher_name):
    """ایمیل HTML برای اعلام نمره — با Retry حرفه‌ای."""
    try:
        _send_html_email(
            subject       = f'🏆 نمره تکلیف: {assignment_title}',
            template_name = 'emails/grade_email.html',
            context       = {
                'student_name':     student_name,
                'teacher_name':     teacher_name,
                'assignment_title': assignment_title,
                'course_title':     course_title,
                'score':            score,
                'max_score':        max_score,
                'feedback':         feedback,
                'assignment_pk':    assignment_pk,
                'site_url':         SITE_URL,
            },
            recipient_email = student_email,
        )
        logger.info(f'✅ ایمیل نمره به {student_email} ارسال شد')
        return f'success:{student_email}'

    except Exception as exc:
        error_msg = str(exc)
        if _is_permanent_error(error_msg):
            return f'permanent_error:{student_email}'
        try:
            raise self.retry(exc=exc, countdown=_get_retry_countdown(self.request.retries))
        except MaxRetriesExceededError:
            logger.critical(f'ایمیل نمره به {student_email} شکست')
            return f'max_retries_exceeded:{student_email}'


@shared_task(
    bind            = True,
    max_retries     = 3,
    soft_time_limit = 30,
    time_limit      = 60,
)
def send_enrollment_email(self, teacher_email, teacher_name,
                          student_name, course_title,
                          course_slug, enrolled_at):
    """ایمیل HTML برای ثبت‌نام جدید — با Retry حرفه‌ای."""
    try:
        _send_html_email(
            subject       = f'👋 ثبت‌نام جدید در {course_title}',
            template_name = 'emails/enrollment_email.html',
            context       = {
                'teacher_name': teacher_name,
                'student_name': student_name,
                'course_title': course_title,
                'course_slug':  course_slug,
                'enrolled_at':  enrolled_at,
                'site_url':     SITE_URL,
            },
            recipient_email = teacher_email,
        )
        logger.info(f'✅ ایمیل ثبت‌نام به {teacher_email} ارسال شد')
        return f'success:{teacher_email}'

    except Exception as exc:
        error_msg = str(exc)
        if _is_permanent_error(error_msg):
            return f'permanent_error:{teacher_email}'
        try:
            raise self.retry(exc=exc, countdown=_get_retry_countdown(self.request.retries))
        except MaxRetriesExceededError:
            logger.critical(f'ایمیل ثبت‌نام به {teacher_email} شکست')
            return f'max_retries_exceeded:{teacher_email}'


@shared_task(
    bind            = True,
    max_retries     = 3,
    soft_time_limit = 30,
    time_limit      = 60,
)
def send_submission_email(self, teacher_email, teacher_name,
                          student_name, assignment_title,
                          course_title, assignment_pk, is_late):
    """ایمیل HTML برای ارسال تکلیف — با Retry حرفه‌ای."""
    try:
        _send_html_email(
            subject       = f'📤 ارسال تکلیف: {assignment_title}',
            template_name = 'emails/submission_email.html',
            context       = {
                'teacher_name':     teacher_name,
                'student_name':     student_name,
                'assignment_title': assignment_title,
                'course_title':     course_title,
                'assignment_pk':    assignment_pk,
                'is_late':          is_late,
                'site_url':         SITE_URL,
            },
            recipient_email = teacher_email,
        )
        logger.info(f'✅ ایمیل ارسال تکلیف به {teacher_email} ارسال شد')
        return f'success:{teacher_email}'

    except Exception as exc:
        error_msg = str(exc)
        if _is_permanent_error(error_msg):
            return f'permanent_error:{teacher_email}'
        try:
            raise self.retry(exc=exc, countdown=_get_retry_countdown(self.request.retries))
        except MaxRetriesExceededError:
            logger.critical(f'ایمیل ارسال تکلیف به {teacher_email} شکست')
            return f'max_retries_exceeded:{teacher_email}'


# ══════════════════════════════════════════════════════════
# تسک‌های Beat (زمان‌بندی‌شده)
# ══════════════════════════════════════════════════════════

@shared_task
def remind_due_assignments():
    """
    هر روز ساعت ۸ صبح — یادآوری تکالیف فردا.
    این تسک نیازی به retry ندارد چون Beat فردا دوباره اجراش می‌کنه.
    """
    from assignments.models import Assignment, Submission
    from courses.models import Enrollment

    now      = timezone.now()
    tomorrow = now + timedelta(hours=24)

    assignments = Assignment.objects.filter(
        due_date__gte=now,
        due_date__lte=tomorrow,
    ).select_related('course', 'teacher')
    count = 0
    for assignment in assignments:
        enrollments = Enrollment.objects.filter(
            course=assignment.course
        ).select_related('student')

        for enrollment in enrollments:
            student = enrollment.student
            already_submitted = Submission.objects.filter(
                assignment=assignment, student=student
            ).exists()

            if not already_submitted and student.email:
                try:
                    _send_html_email(
                        subject       = '⏰ یادآوری: مهلت تکلیف فردا تموم میشه',
                        template_name = 'emails/reminder_email.html',
                        context       = {
                            'student_name':     student.get_full_name() or student.username,
                            'assignment_title': assignment.title,
                            'course_title':     assignment.course.title,
                            'due_date':         assignment.due_date.strftime('%Y/%m/%d %H:%M'),
                            'assignment_pk':    assignment.pk,
                            'site_url':         SITE_URL,
                            'reminder_type':    'tomorrow',
                        },
                        recipient_email = student.email,
                    )
                    from notifications.utils import send_notification
                    send_notification(
                        recipient  = student,
                        notif_type = 'assignment',
                        title      = f'⏰ یادآوری: {assignment.title}',
                        message    = f'مهلت تکلیف «{assignment.title}» فردا تموم میشه!',
                        link       = f'/assignments/{assignment.pk}/',
                    )
                    count += 1
                    logger.info(f'✅ یادآوری فردا به {student.email}')
                except Exception as e:
                    logger.error(f'❌ خطا در یادآوری فردا: {e}')

    return f'{count} یادآوری فردا ارسال شد'


@shared_task
def remind_due_today():
    """هر روز ساعت ۱۰ صبح — آخرین فرصت امروز."""
    from assignments.models import Assignment, Submission
    from courses.models import Enrollment

    now        = timezone.now()
    end_of_day = now.replace(hour=23, minute=59, second=59)

    assignments = Assignment.objects.filter(
        due_date__gte=now,
        due_date__lte=end_of_day,
    ).select_related('course', 'teacher')

    count = 0
    for assignment in assignments:
        enrollments = Enrollment.objects.filter(
            course=assignment.course
        ).select_related('student')

        for enrollment in enrollments:
            student = enrollment.student
            already_submitted = Submission.objects.filter(
                assignment=assignment, student=student
            ).exists()

            if not already_submitted and student.email:
                try:
                    _send_html_email(
                        subject       = '🚨 آخرین فرصت: مهلت تکلیف امروز!',
                        template_name = 'emails/reminder_email.html',
                        context       = {
                            'student_name':     student.get_full_name() or student.username,
                            'assignment_title': assignment.title,
                            'course_title':     assignment.course.title,
                            'due_date':         assignment.due_date.strftime('%Y/%m/%d %H:%M'),
                            'assignment_pk':    assignment.pk,
                            'site_url':         SITE_URL,
                            'reminder_type':    'today',
                        },
                        recipient_email = student.email,
                    )
                    from notifications.utils import send_notification
                    send_notification(
                        recipient  = student,
                        notif_type = 'assignment',
                        title      = f'🚨 آخرین فرصت: {assignment.title}',
                        message    = f'مهلت تکلیف «{assignment.title}» امروز تموم میشه!',
                        link       = f'/assignments/{assignment.pk}/',
                    )
                    count += 1
                    logger.info(f'✅ یادآوری امروز به {student.email}')
                except Exception as e:
                    logger.error(f'❌ خطا در یادآوری امروز: {e}')

    return f'{count} یادآوری امروز ارسال شد'


@shared_task
def weekly_teacher_report():
    """هر دوشنبه ساعت ۹ صبح — گزارش هفتگی به اساتید."""
    from accounts.models import User
    from assignments.models import Submission
    from courses.models import Course, Enrollment

    teachers     = User.objects.filter(role='teacher')
    now          = timezone.now()
    one_week_ago = now - timedelta(days=7)
    count        = 0

    for teacher in teachers:
        if not teacher.email:
            continue

        courses = Course.objects.filter(teacher=teacher)
        if not courses.exists():
            continue

        new_submissions = Submission.objects.filter(
            assignment__course__in=courses,
            submitted_at__gte=one_week_ago,
        ).count()

        pending_grade = Submission.objects.filter(
            assignment__course__in=courses,
            status='submitted',
        ).count()

        new_enrollments = Enrollment.objects.filter(
            course__in=courses,
            enrolled_at__gte=one_week_ago,
        ).count()

        if new_submissions == 0 and new_enrollments == 0:
            continue

        try:
            _send_html_email(
                subject       = f'📊 گزارش هفتگی — {now.strftime("%Y/%m/%d")}',
                template_name = 'emails/weekly_report_email.html',
                context       = {
                    'teacher_name':    teacher.get_full_name() or teacher.username,
                    'new_submissions': new_submissions,
                    'pending_grade':   pending_grade,
                    'new_enrollments': new_enrollments,
                    'total_courses':   courses.count(),
                    'site_url':        SITE_URL,
                    'week_start':      one_week_ago.strftime('%Y/%m/%d'),
                    'week_end':        now.strftime('%Y/%m/%d'),
                },
                recipient_email = teacher.email,
            )
            count += 1
            logger.info(f'✅ گزارش هفتگی به {teacher.email}')
        except Exception as e:
            logger.error(f'❌ خطا در گزارش هفتگی برای {teacher.email}: {e}')

    return f'گزارش هفتگی به {count} استاد ارسال شد'

@shared_task(
    bind            = True,
    max_retries     = 3,
    soft_time_limit = 30,
    time_limit      = 60,
)

def send_welcom_email(self, user_email, user_name, role, site_url):
    try:
        _send_html_email(
            subject  = '🎓 خوش آمدید به سامانه آموزش آنلاین',
            template_name='emails/welcom_email.html',
            context  = {
                'user_name':user_name,
                'role':role,
                'site_url':site_url
            },
            recipient_email='user_email'
        )
        logger.info(f'✅ ایمیل خوش‌آمد به {user_email} ارسال شد')
        return f'success:{user_email}'


    except Exception as exc:
        error_msg = str(exc)
        if _is_permanent_error(error_msg):
            return f"permanent_error:{user_email}"

    except MaxRetriesExceededError:
        logger.critical

    try:
        raise self.retry(
            exc       = exc,
            countdown = _get_retry_countdown(self.request.retries)
            )
    except MaxRetriesExceededError:
        logger.critical(f'ایمیل خوش‌آمد به {user_email} شکست')
        return f'max_retries_exceeded:{user_email}'