import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from cases.models import Case, CaseAuditLog, Report
from accounts.models import CustomUser as User


@login_required
def dashboard(request):
    user = request.user
    context = {'user_role': None}

    if user.is_superuser or user.groups.filter(name='Admin').exists():
        pending_reports = Report.objects.filter(is_approved=False)
        context.update({
            'user_role': 'Admin',
            'total_cases': Case.objects.count(),
            'total_users': User.objects.count(),
            'open_cases': Case.objects.filter(~Q(status='CLOSED')).count(),
            'pending_approvals': Case.objects.filter(status='PENDING_REVIEW').count(),
            'active_cases': Case.objects.filter(status='IN_PROGRESS').count(),
            'pending_reports': pending_reports.count(),
            'approved_week_count': Report.objects.filter(is_approved=True, date_submitted__gte=timezone.now()-timedelta(days=7)).count(),
        })
        context['recent_cases'] = Case.objects.select_related('created_by', 'technician').order_by('-created_at')[:10]
    elif user.groups.filter(name='Technician').exists():
        my_cases_qs = Case.objects.filter(technician=user)
        context.update({
            'user_role': 'Technician',
            'my_cases_count': my_cases_qs.count(),
            'assigned_count': my_cases_qs.filter(status='ASSIGNED').count(),
            'in_progress_count': my_cases_qs.filter(status='IN_PROGRESS').count(),
            'closed_week_count': my_cases_qs.filter(status='CLOSED', updated_at__gte=timezone.now()-timedelta(days=7)).count(),
        })
        context['recent_cases'] = my_cases_qs.select_related('created_by', 'technician').order_by('-created_at')[:10]
    else:
        user_cases = Case.objects.filter(created_by=user)
        context.update({
            'user_role': 'Student',
            'my_cases_count': user_cases.count(),
            'open_cases': user_cases.exclude(status='CLOSED').count(),
            'resolved_cases': user_cases.filter(status='CLOSED').count(),
        })
        context['recent_cases'] = user_cases.select_related('created_by', 'technician').order_by('-created_at')[:10]

    return render(request, 'dashboard/dashboard.html', context)  
        