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
        return f"{self.get_full_name()} ({self.get_role_display()})"