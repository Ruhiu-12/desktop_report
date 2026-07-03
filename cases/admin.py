from django.contrib import admin
from .models import Case, CaseAuditLog

admin.site.register(Case)
admin.site.register(CaseAuditLog)

# Register your models here.
