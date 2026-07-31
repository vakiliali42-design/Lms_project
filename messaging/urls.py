# messaging/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('',
         views.conversation_list,   name='conversation_list'),

    path('<int:pk>/',
         views.conversation_detail, name='conversation_detail'),

    path('start/<int:user_pk>/',
         views.start_conversation,  name='start_conversation'),

    path('message/<int:pk>/delete/',
         views.delete_message,      name='delete_message'),
]