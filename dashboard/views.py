import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from cases.models import Case, CaseAuditLog
from accounts.models import CustomUser as User


@login_required
def dashboard(request):
    user = request.user
    context = {'user_role': None}

    if user.is_superuser:
        context.update({
            'user_role': 'superadmin',
            'total_cases': Case.objects.count(),
            'total_users': User.objects.count(),
            'open_cases': Case.objects.filter(~Q(status='CLOSED')).count(),
            'recent_audit_logs': CaseAuditLog.objects.order_by('-timestamp')[:10],  # Assuming you have a CaseAuditLog model for audit logs
        })
    elif user.groups.filter(name='admin').exists():
        context.update({
            'user_role': 'admin',
            'pending_approvals': Case.objects.filter(status='PENDING_REVIEW').count(),
            'active_cases': Case.objects.filter(status='IN_PROGRESS').count(),
        })
    elif user.groups.filter(name='technician').exists():
        context.update({
            'user_role': 'technician',
            'my_cases': Case.objects.filter(technician=user).count(),
            'assigned_to_me': Case.objects.filter(technician=user, status='ASSIGNED').count(),
        })
    elif user.groups.filter(name='analyst').exists():
        context.update({
            'user_role': 'analyst',
            'pending_analysis': Case.objects.filter(status='NEW').count(),
        })
    else:
        user_cases = Case.objects.filter(created_by=user)
        context.update({
            'user_role': 'user',
            'my_cases': user_cases.count(),
            'open_cases': user_cases.exclude(status='CLOSED').count(),
        })

    context['recent_cases'] = Case.objects.select_related('created_by', 'technician').order_by('-created_at')[:5]

    return render(request, 'dashboard/dashboard.html', context)  
        