# assignments/models.py

from django.db import models
from accounts.models import User
from courses.models import Course

class Assignment(models.Model):
    course      = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    teacher     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_assignments')
    title       = models.CharField(max_length=200)
    description = models.TextField()
    file        = models.FileField(upload_to='assignments/files/', blank=True, null=True)
    due_date    = models.DateTimeField()
    max_score   = models.PositiveIntegerField(default=100)
    created_at  = models.DateTimeField(auto_now_add=True)

    def str(self): return f"{self.course.title} — {self.title}"

class Submission(models.Model):
    STATUS_CHOICES = (('submitted','ارسال شده'), ('graded','نمره‌دهی شده'), ('late','دیر ارسال'))

    assignment  = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    file        = models.FileField(upload_to='submissions/')
    note        = models.TextField(blank=True)
    score       = models.PositiveIntegerField(null=True, blank=True)
    feedback    = models.TextField(blank=True)
    status      = models.CharField(max_length=15, choices=STATUS_CHOICES, default='submitted')
    submitted_at= models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('assignment', 'student')

    def str(self): return f"{self.student} → {self.assignment.title}"