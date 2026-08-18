from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_async_email(self, subject, template_name, context, recipient_list):
    """
    وظیفه عمومی ارسال ایمیل غیرهمزمان با قابلیت Retry خودکار و پشتیبانی از HTML
    """
    try:
        html_content = render_to_string(template_name, context)
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_list
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        logger.info(f"Email '{subject}' successfully sent to {recipient_list}")
        return True
    except Exception as exc:
        logger.error(f"Error sending email '{subject}' to {recipient_list}: {exc}")
        # تلاش مجدد با فاصله زمانی در صورت بروز خطای شبکه یا SMTP
        raise self.retry(exc=exc)