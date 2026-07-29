# adminpanel/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # داشبورد
    path('', views.admin_dashboard, name='admin_dashboard'),

    # کاربران
    path('users/',                    views.user_list,          name='admin_user_list'),
    path('users/create/',             views.user_create,        name='admin_user_create'),
    path('users/<int:pk>/edit/',      views.user_edit,          name='admin_user_edit'),
    path('users/<int:pk>/toggle/',    views.user_toggle_active, name='admin_user_toggle'),
    path('users/<int:pk>/delete/',    views.user_delete,        name='admin_user_delete'),

    # دوره‌ها
    path('courses/',                  views.course_list_admin,    name='admin_course_list'),
    path('courses/<int:pk>/publish/', views.course_toggle_publish, name='admin_course_publish'),
    path('courses/<int:pk>/edit/',    views.course_edit_admin,    name='admin_course_edit'),
    path('courses/<int:pk>/delete/',  views.course_delete_admin,  name='admin_course_delete'),

    # تکالیف
    path('assignments/',
         views.assignment_list_admin, name='admin_assignment_list'),
    path('assignments/<int:assignment_pk>/submissions/',
         views.submission_list_admin, name='admin_submission_list'),
    path('submissions/<int:pk>/delete/',
         views.submission_delete_admin, name='admin_submission_delete'),
]