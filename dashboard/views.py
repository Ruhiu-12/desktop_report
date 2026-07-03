import json
from multiprocessing import context
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncDate
from .decorators import role_required

# Import your project models
from cases.models import Case, CaseAuditLog
from accounts.models import CustomUser as User




@login_required
def dashboard(request):
    user = request.user
    
    # 1. Superuser Logic
    if user.is_superuser:
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        case_status_counts = dict(Case.objects.values('status').annotate(count=Count('id')).values_list('status', 'count'))
        case_priority_counts = dict(Case.objects.values('case_priority').annotate(count=Count('id')).values_list('case_priority', 'count'))
        
        cases_by_date = list(Case.objects.filter(created_at__gte=thirty_days_ago).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(count=Count('id')).order_by('date'))
        
        context = {
            'user_role': 'Superuser',
            'is_superuser': True,
            'total_cases': Case.objects.count(),
            'total_users': User.objects.count(),
            'case_status_counts': json.dumps(case_status_counts),
            'case_priority_counts': json.dumps(case_priority_counts),
            'cases_by_date': json.dumps({str(item['date']): item['count'] for item in cases_by_date}),
            'recent_cases': Case.objects.all().order_by('-created_at')[:5],
            'recent_audit_logs': CaseAuditLog.objects.all().order_by('-timestamp')[:5],
        }
        return render(request, 'dashboard/partials/superadmin_stats.html', context)
       
    # # --- ADMIN LOGIC (Operational, not Infrastructure) ---
    # elif role == 'admin':
    #     context.update({
    #         'pending_approvals': Case.objects.filter(status='PENDING').count(),
    #         'total_active': Case.objects.filter(status='IN_PROGRESS').count(),
    #         'recent_cases': Case.objects.all().order_by('-created_at  ')[:5],
    #         # Add other operational metrics relevant to an Admin here
    #     })

    # return render(request, 'dashboard/dashboard.html', context)

    # Role-Specific View Logic
   # 2. ADMIN: Operational metrics
    elif user.groups.filter(name='admin').exists():
        admin_context = {
            'pending_approvals': Case.objects.filter(status='PENDING').count(),
            'total_active': Case.objects.filter(status='IN_PROGRESS').count(),
            'recent_cases': Case.objects.all().order_by('-created_at')[:5],
        }
        return render(request, 'dashboard/partials/admin_stats.html', admin_context)

    # 3. ANALYST: Forensic focus
    elif user.groups.filter(name='analyst').exists():
        # Analyst: Focus on forensic throughput and analysis
        analyst_context =            {
            'total_cases': Case.objects.count(),
            'cases_needing_analysis': Case.objects.filter(status='NEEDS_ANALYSIS').count(),
            'recent_cases': Case.objects.all().order_by('-created_at')[:5],
            'pending_reports': Case.objects.filter(status='REPORT_PENDING').count(),
        }
        return render(request, 'dashboard/partials/analyst_stats.html', analyst_context)                            
      

    

    # 5. TECHNICIAN: Technical support cases
    elif user.groups.filter(name='technician').exists():
        technician_context =         {
            'total_cases': Case.objects.count(),
            'cases_needing_tech_support': Case.objects.filter(case_status='TECH_SUPPORT').count(),
            'recent_cases': Case.objects.all().order_by('-created_at')[:5],
        }
        return render(request, 'dashboard/partials/technician_stats.html', technician_context)  

    # 6. FALLBACK: Personal contributions
    else:
        user_cases = Case.objects.filter(created_by=user)
        user_context =         {
            'total_cases': user_cases.count(),
            'recent_cases': user_cases.order_by('-created_at')[:5],
        }
        return render(request, 'dashboard/partials/user_stats.html', user_context)  
        