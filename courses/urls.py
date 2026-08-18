from django.urls import path
from . import views

urlpatterns = [
    path("", views.course_list, name="course_list"),
    path("create/", views.create_course, name="create_course"),
    path("search/", views.global_search, name="global_search"),
    path("<slug:slug>/", views.course_detail, name="course_detail"),
    path("<slug:slug>/enroll/", views.enroll_course, name="enroll_course"),
    path("<slug:slug>/add-lesson/", views.add_lesson, name="add_lesson"),
    path("<slug:slug>/upload/", views.upload_content, name="upload_content"),
    path("<slug:slug>/review/", views.add_review, name="add_review"),
    path("<slug:slug>/review/<int:pk>/remove/", views.remove_review, name="delete_review"),
    path("edit/<slug:slug>/", views.edit_course, name="edit_course"),
    path("<slug:slug>/students/", views.course_students, name="course_students"),
    path("lesson/<int:pk>/edit/", views.edit_lesson, name="edit_lesson"),
    path("lesson/<int:pk>/delete/", views.delete_lesson, name="delete_lesson"),
    path("teacher/<int:pk>/", views.teacher_profile, name="teacher_profile"),
]