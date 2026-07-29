# lms_project/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import dashboard_view
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/',        admin.site.urls),
    path('',              TemplateView.as_view(template_name='home.html'), name='home'),
    path('dashboard/',    dashboard_view, name='dashboard'),
    path('accounts/',     include('accounts.urls')),
    path('courses/',      include('courses.urls')),
    path('assignments/',  include('assignments.urls')),
    path('notifications/', include('notifications.urls')),
    path('adminpanel/', include("adminpanel.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)