from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden
from cases.models import Case, Report, CaseAuditLog
from .forms import ReportCreateForm


@login_required
def report_list(request):
    user = request.user
    queryset = Report.objects.select_related('case', 'technician')

    if user.is_superuser or user.groups.filter(name='admin').exists():
        pass
    elif user.groups.filter(name='technician').exists():
        queryset = queryset.filter(technician=user)
    elif user.groups.filter(name='analyst').exists():
        pass
    else:
        queryset = queryset.none()

    search_query = request.GET.get('search', '').strip()
    if search_query:
        queryset = queryset.filter(
            Q(case__title__icontains=search_query)
            | Q(technician__identifier__icontains=search_query)
            | Q(findings__icontains=search_query)
        )

    status_filter = request.GET.get('status', '')
    if status_filter == 'approved':
        queryset = queryset.filter(is_approved=True)
    elif status_filter == 'pending':
        queryset = queryset.filter(is_approved=False)

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'reports/report_list.html', context)


@login_required
def report_detail(request, report_id):
    report = get_object_or_404(
        Report.objects.select_related('case', 'technician', 'case__created_by'),
        id=report_id,
    )
    user = request.user

    if not (
        user.is_superuser
        or user.groups.filter(name='admin').exists()
        or report.technician == user
        or user.groups.filter(name='analyst').exists()
    ):
        return HttpResponseForbidden("You do not have permission to view this report.")

    can_review = (
        user.is_superuser
        or user.groups.filter(name='admin').exists()
        or user.groups.filter(name='analyst').exists()
    )

    context = {
        'report': report,
        'can_review': can_review,
    }
    return render(request, 'reports/report_detail.html', context)


@login_required
def report_create(request, case_id):
    case = get_object_or_404(Case, id=case_id)
    user = request.user

    if case.technician != user:
        return HttpResponseForbidden("Only the assigned technician can create a report for this case.")

    if Report.objects.filter(case=case).exists():
        messages.error(request, 'A report already exists for this case.')
        return redirect('report_list')

    if request.method == 'POST':
        form = ReportCreateForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.case = case
            report.technician = user
            report.save()

            case.status = 'PENDING_REVIEW'
            case.save()

            CaseAuditLog.objects.create(
                case=case,
                action=f'Report submitted by {user.identifier}',
                changed_by=user,
            )
            messages.success(request, 'Report submitted successfully.')
            return redirect('report_detail', report_id=report.id)
    else:
        form = ReportCreateForm()

    context = {
        'form': form,
        'case': case,
    }
    return render(request, 'reports/report_create.html', context)


@login_required
def report_review(request, report_id):
    report = get_object_or_404(Report.objects.select_related('case'), id=report_id)
    user = request.user

    if not (
        user.is_superuser
        or user.groups.filter(name='admin').exists()
        or user.groups.filter(name='analyst').exists()
    ):
        return HttpResponseForbidden("Only analysts can review reports.")

    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action == 'approve':
            report.is_approved = True
            report.save()
            report.case.status = 'CLOSED'
            report.case.save()
            CaseAuditLog.objects.create(
                case=report.case,
                action=f'Report approved by {user.identifier} - Case closed',
                changed_by=user,
            )
            messages.success(request, 'Report approved. Case has been closed.')
        elif action == 'reject':
            report.is_approved = False
            report.save()
            report.case.status = 'IN_PROGRESS'
            report.case.save()
            CaseAuditLog.objects.create(
                case=report.case,
                action=f'Report rejected by {user.identifier} - Case reopened to IN_PROGRESS',
                changed_by=user,
            )
            messages.warning(request, 'Report rejected. Case sent back to In Progress.')
        return redirect('report_detail', report_id=report.id)

    return redirect('report_detail', report_id=report.id)
