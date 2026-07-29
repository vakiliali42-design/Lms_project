# courses/admin.py
from django.contrib import admin
from .models import Course, Lesson, Enrollment, Category, CourseContent

admin.site.register(Category)
admin.site.register(CourseContent)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display  = ['title', 'teacher', 'level', 'is_published', 'created_at']
    list_filter   = ['level', 'is_published']
    prepopulated_fields = {'slug': ('title',)}

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrolled_at', 'completed']