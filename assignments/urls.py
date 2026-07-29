from django.urls import path
from . import views

urlpatterns = [
    path('course/<slug:course_slug>/',
         views.assignment_list,    name='assignment_list'),

    path('course/<slug:course_slug>/create/',
         views.create_assignment,  name='create_assignment'),

    path('<int:pk>/',
         views.assignment_detail,  name='assignment_detail'),

    path('<int:pk>/edit/',
         views.edit_assignment,    name='edit_assignment'),

    path('<int:pk>/submit/',
         views.submit_assignment,  name='submit_assignment'),

    path('submission/<int:pk>/grade/',
         views.grade_submission,   name='grade_submission'),
]