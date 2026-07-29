# notifications/models.py

from django.db import models
from accounts.models import User

class Notification(models.Model):
    TYPE_CHOICES = (
        ('assignment', 'تکلیف جدید'),
        ('submission', 'ارسال تکلیف'),
        ('grade',      'نمره‌دهی'),
        ('enroll',     'ثبت‌نام'),
    )

    recipient   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notif_type  = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title       = models.CharField(max_length=200)
    message     = models.TextField()
    link        = models.CharField(max_length=300, blank=True)
    is_read     = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def str(self):
        return f"{self.recipient.username} — {self.title}"