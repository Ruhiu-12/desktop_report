from django.contrib import admin
from .models import ActivityLog, Feedback

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'description', 'ip_address')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__identifier', 'description')
    readonly_fields = ('user', 'action', 'description', 'ip_address', 'timestamp')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'submitted_by', 'status', 'created_at')
    list_filter = ('type', 'status', 'created_at')
    search_fields = ('title', 'description', 'submitted_by__identifier')
    readonly_fields = ('submitted_by', 'created_at', 'updated_at')
