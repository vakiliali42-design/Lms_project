from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

urlpatterns = [

    # ── Auth ─────────────────────────────────────────────
    path('auth/register/',
         views.RegisterView.as_view(),   name='api_register'),
    path('auth/login/',
         TokenObtainPairView.as_view(),  name='api_login'),
    path('auth/refresh/',
         TokenRefreshView.as_view(),     name='api_refresh'),
    path('auth/profile/',
         views.ProfileView.as_view(),    name='api_profile'),

    # ── Courses ───────────────────────────────────────────
    path('courses/',
         views.CourseListView.as_view(),    name='api_course_list'),
    path('courses/create/',
         views.CourseCreateView.as_view(),  name='api_course_create'),
    path('courses/my/',
         views.MyCoursesView.as_view(),     name='api_my_courses'),
    path('courses/teaching/',
         views.TeacherCoursesView.as_view(),name='api_teaching'),
    path('courses/<slug:slug>/',
         views.CourseDetailView.as_view(),  name='api_course_detail'),
    path('courses/<slug:slug>/edit/',
         views.CourseUpdateView.as_view(),  name='api_course_edit'),
    path('courses/<slug:slug>/enroll/',
         views.EnrollView.as_view(),        name='api_enroll'),

    # ── Assignments ───────────────────────────────────────
    path('assignments/',
         views.AssignmentListView.as_view(),   name='api_assignment_list'),
    path('assignments/create/',
         views.AssignmentCreateView.as_view(), name='api_assignment_create'),
    path('assignments/<int:pk>/submit/',
         views.SubmitAssignmentView.as_view(), name='api_submit'),
    path('assignments/<int:pk>/submissions/',
         views.SubmissionListView.as_view(),   name='api_submissions'),
    path('assignments/submission/<int:pk>/grade/',
         views.GradeSubmissionView.as_view(),  name='api_grade'),

    # ── Notifications ─────────────────────────────────────
    path('notifications/',
         views.NotificationListView.as_view(), name='api_notifs'),
    path('notifications/read-all/',
         views.MarkAllReadView.as_view(),       name='api_read_all'),
    path('notifications/<int:pk>/read/',
         views.MarkReadView.as_view(),          name='api_read'),
]