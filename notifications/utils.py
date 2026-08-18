from .models import Notification


def send_notification(recipient, notif_type, title, message, link=''):
    Notification.objects.create(
        recipient  = recipient,
        notif_type = notif_type,
        title      = title,
        message    = message,
        link       = link,
    )


def notify_new_assignment(assignment):
    from courses.models import Enrollment
    from notifications.tasks import send_assignment_email

    enrollments = Enrollment.objects.filter(
        course=assignment.course
    ).select_related('student')

    for enrollment in enrollments:
        student = enrollment.student
        send_notification(
            recipient  = student,
            notif_type = 'assignment',
            title      = f'تکلیف جدید: {assignment.title}',
            message    = f'استاد {assignment.teacher.get_full_name()} '
                         f'تکلیف جدیدی در دوره «{assignment.course.title}» '
                         f'با مهلت {assignment.due_date.strftime("%Y/%m/%d")} ثبت کرد.',
            link       = f'/assignments/{assignment.pk}/',
        )
        if student.email:
            send_assignment_email.delay(
                student_email    = student.email,
                student_name     = student.get_full_name() or student.username,
                course_title     = assignment.course.title,
                assignment_title = assignment.title,
                due_date         = assignment.due_date.strftime('%Y/%m/%d'),
                max_score        = assignment.max_score,
                description      = assignment.description,
                assignment_pk    = assignment.pk,
                teacher_name     = assignment.teacher.get_full_name() or assignment.teacher.username,
            )


def notify_submission_received(submission):
    from notifications.tasks import send_submission_email

    teacher = submission.assignment.teacher
    is_late = submission.status == 'late'

    send_notification(
        recipient  = teacher,
        notif_type = 'submission',
        title      = f'ارسال تکلیف: {submission.assignment.title}',
        message    = f'دانشجو {submission.student.get_full_name()} '
                     f'تکلیف «{submission.assignment.title}» را ارسال کرد.',
        link       = f'/assignments/{submission.assignment.pk}/',
    )
    if teacher.email:
        send_submission_email.delay(
            teacher_email    = teacher.email,
            teacher_name     = teacher.get_full_name() or teacher.username,
            student_name     = submission.student.get_full_name() or submission.student.username,
            assignment_title = submission.assignment.title,
            course_title     = submission.assignment.course.title,
            assignment_pk    = submission.assignment.pk,
            is_late          = is_late,
        )


def notify_grade_given(submission):
    from notifications.tasks import send_grade_email

    student = submission.student
    send_notification(
        recipient  = student,
        notif_type = 'grade',
        title      = f'نمره ثبت شد: {submission.assignment.title}',
        message    = f'استاد {submission.assignment.teacher.get_full_name()} '
                     f'به تکلیف شما نمره {submission.score} داد.'
                     + (f'\nبازخورد: {submission.feedback}' if submission.feedback else ''),
        link       = f'/assignments/{submission.assignment.pk}/',
    )
    if student.email:
        send_grade_email.delay(
            student_email    = student.email,
            student_name     = student.get_full_name() or student.username,
            assignment_title = submission.assignment.title,
            course_title     = submission.assignment.course.title,
            score            = submission.score,
            max_score        = submission.assignment.max_score,
            feedback         = submission.feedback,
            assignment_pk    = submission.assignment.pk,
            teacher_name     = submission.assignment.teacher.get_full_name() or
                               submission.assignment.teacher.username,
        )


def notify_enrollment(enrollment):
    from notifications.tasks import send_enrollment_email

    teacher = enrollment.course.teacher
    send_notification(
        recipient  = teacher,
        notif_type = 'enroll',
        title      = f'ثبت‌نام جدید در {enrollment.course.title}',
        message    = f'دانشجو {enrollment.student.get_full_name()} '
                     f'در دوره «{enrollment.course.title}» ثبت‌نام کرد.',
        link       = f'/courses/{enrollment.course.slug}/',
    )
    if teacher.email:
        send_enrollment_email.delay(
            teacher_email = teacher.email,
            teacher_name  = teacher.get_full_name() or teacher.username,
            student_name  = enrollment.student.get_full_name() or enrollment.student.username,
            course_title  = enrollment.course.title,
            course_slug   = enrollment.course.slug,
            enrolled_at   = enrollment.enrolled_at.strftime('%Y/%m/%d %H:%M'),
        )