from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', "دانشجو"),
        ('teacher', "استاد"),
        ('admin', "ادمین"),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_student(self):
        return self.role == "student"

    def is_teacher(self):
        return self.role == "teacher"

    def is_admin(self):
        return self.role == "admin"

    def __str__(self):
        full_name = self.get_full_name().strip()

        if full_name:
            return f"{full_name} ({self.get_role_display()})"

        if self.username:
            return f"{self.username} ({self.get_role_display()})"

        return self.email

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = 'admin'
        super().save(*args, **kwargs)
