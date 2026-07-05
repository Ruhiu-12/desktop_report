from django.contrib import admin
from cases.models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('case', 'technician', 'date_submitted', 'is_approved')
    list_filter = ('is_approved', 'date_submitted')
    search_fields = ('case__title', 'technician__identifier', 'findings')
