# lms_project/celery.py

import os
from celery import Celery
from celery.signals import task_success, task_failure, task_retry

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_project.settings')

app = Celery('lms_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


# ── Signals — لاگ خودکار برای همه تسک‌ها ────────────────

@task_success.connect
def on_task_success(sender, result, **kwargs):
    """
    وقتی هر تسکی موفق میشه این تابع صدا زده میشه.
    در Flower به عنوان SUCCESS نشون داده میشه.
    """
    import logging
    logger = logging.getLogger('celery')
    logger.info(f'✅ تسک موفق: {sender.name} → {result}')


@task_failure.connect
def on_task_failure(sender, exception, **kwargs):
    """
    وقتی هر تسکی شکست می‌خوره این تابع صدا زده میشه.
    در Flower به عنوان FAILURE با رنگ قرمز نشون داده میشه.
    """
    import logging
    logger = logging.getLogger('celery')
    logger.error(f'❌ تسک شکست: {sender.name} → {exception}')


@task_retry.connect
def on_task_retry(sender, reason, **kwargs):
    """
    وقتی retry اتفاق میفته این تابع صدا زده میشه.
    در Flower به عنوان RETRY نشون داده میشه.
    """
    import logging
    logger = logging.getLogger('celery')
    logger.warning(f'🔄 تسک retry: {sender.name} → {reason}')