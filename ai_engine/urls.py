from django.urls import path
from . import views

urlpatterns = [
    path('recommendations/', views.recommendations_view, name='recommendations'),
    path('plagiarism/<int:assignment_pk>/', views.plagiarism_check_view, name='plagiarism_check'),
]
