from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class Notification(admin.ModelAdmin):
    list_display = ['recipient','notif_type', 'message', 'title', 'is_read', 'created_at']
    list_filter = ['notif_type', 'is_read', 'created_at']
    search_fields = ['recipient__username', 'message', 'title']
