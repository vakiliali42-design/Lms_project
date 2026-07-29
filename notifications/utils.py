from .models import Notification

#help function to create a notification
def send_notification(recipient, notif_type, title, message, link=''):
    Notification.objects.create(
        recipient=recipient,
        notif_type=notif_type,
        title=title,
        message=message,
        link=link,
    )
    
#tell the students that an upload happened
def notify_new_assignment(assignment):
    from courses.models import Enrollment
    enrollments = Enrollment.objects.filter(
        course=assignment.course
    ).select_related('student')

    for enrollment in enrollments:
        send_notification(
            recipient=enrollment.student,
            notif_type='assignment',
            title=f'تکلیف جدید: {assignment.title}',
            message=f'استاد {assignment.teacher.get_full_name()} '
                    f'تکلیف جدیدی در دوره «{assignment.course.title}» '
                    f'با مهلت {assignment.due_date.strftime("%Y/%m/%d")} ثبت کرد.',
            link=f'/assignments/{assignment.pk}/',
        )

#tell the teachers that the uploading has happened
def notify_submission_received(submission):
    send_notification(
        recipient=submission.assignment.teacher,
        notif_type='submission',
        title=f'ارسال تکلیف: {submission.assignment.title}',
        message=f'دانشجو {submission.student.get_full_name()} '
                f'تکلیف «{submission.assignment.title}» را ارسال کرد.',
        link=f'/assignments/{submission.assignment.pk}/',
    )

#tell the students that their submission has been graded
def notify_grade_given(submission):
    send_notification(
        recipient=submission.student,
        notif_type='grade',
        title=f'نمره ثبت شد: {submission.assignment.title}',
        message=f'استاد {submission.assignment.teacher.get_full_name()} '
                f'به تکلیف شما نمره {submission.score} داد.'
                + (f'\nبازخورد: {submission.feedback}' if submission.feedback else ''),
        link=f'/assignments/{submission.assignment.pk}/',
    )

#tell the teacher that the student enrolled
def notify_enrollment(enrollment):
    send_notification(
        recipient=enrollment.course.teacher,
        notif_type='enroll',
        title=f'ثبت‌نام جدید در {enrollment.course.title}',
        message=f'دانشجو {enrollment.student.get_full_name()} '
                f'در دوره «{enrollment.course.title}» ثبت‌نام کرد.',
        link=f'/courses/{enrollment.course.slug}/',
    )