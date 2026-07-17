from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden
from cases.models import Case, Report, CaseAuditLog, ReportImage
from .forms import ReportCreateForm


@login_required
def report_list(request):
    user = request.user
    queryset = Report.objects.select_related('case', 'technician')

    if user.is_superuser or user.groups.filter(name='Admin').exists():
        pass
    elif user.groups.filter(name='Technician').exists():
        queryset = queryset.filter(technician=user)
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
        or user.groups.filter(name='Admin').exists()
        or report.technician == user
    ):
        return HttpResponseForbidden("You do not have permission to view this report.")

    can_review = (
        user.is_superuser
        or user.groups.filter(name='Admin').exists()
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

    existing_report = Report.objects.filter(case=case).first()

    if existing_report:
        if request.method == 'POST':
            form = ReportCreateForm(request.POST, instance=existing_report)
            if form.is_valid():
                report = form.save()
                case.status = 'PENDING_REVIEW'
                case.save()

                images = request.FILES.getlist('images')
                for img in images:
                    ReportImage.objects.create(report=report, image=img)

                if not images:
                    single = request.FILES.get('image')
                    if single:
                        ReportImage.objects.create(report=report, image=single)

                CaseAuditLog.objects.create(
                    case=case,
                    action=f'Report updated by {user.identifier}',
                    changed_by=user,
                )
                messages.success(request, 'Report updated successfully.')
                return redirect('report_detail', report_id=report.id)
        else:
            form = ReportCreateForm(instance=existing_report)
    else:
        if request.method == 'POST':
            form = ReportCreateForm(request.POST)
            if form.is_valid():
                report = form.save(commit=False)
                report.case = case
                report.technician = user
                report.save()

                images = request.FILES.getlist('images')
                for img in images:
                    ReportImage.objects.create(report=report, image=img)

                if not images:
                    single = request.FILES.get('image')
                    if single:
                        ReportImage.objects.create(report=report, image=single)

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
        'existing_report': existing_report,
    }
    return render(request, 'reports/report_create.html', context)


@login_required
def report_review(request, report_id):
    report = get_object_or_404(Report.objects.select_related('case'), id=report_id)
    user = request.user

    if not (
        user.is_superuser
        or user.groups.filter(name='Admin').exists()
    ):
        return HttpResponseForbidden("Only admins can review reports.")

    if request.method == 'POST':
        action = request.POST.get('action', '')
        if action == 'approve':
            report.is_approved = True
            report.save()
            report.case.status = 'CLOSED'
            report.case.save()

            # Update machine status to HEALTHY when case is closed
            if report.case.asset_tag:
                from labs.models import Machine
                try:
                    machine = Machine.objects.get(name=report.case.asset_tag)
                    machine.status = 'HEALTHY'
                    machine.save()
                except Machine.DoesNotExist:
                    pass

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

            # Update machine status to IN_REPAIR when rejected
            if report.case.asset_tag:
                from labs.models import Machine
                try:
                    machine = Machine.objects.get(name=report.case.asset_tag)
                    machine.status = 'IN_REPAIR'
                    machine.save()
                except Machine.DoesNotExist:
                    pass

            CaseAuditLog.objects.create(
                case=report.case,
                action=f'Report rejected by {user.identifier} - Case reopened to IN_PROGRESS',
                changed_by=user,
            )
            messages.warning(request, 'Report rejected. Case sent back to In Progress.')
        return redirect('report_detail', report_id=report.id)

    return redirect('report_detail', report_id=report.id)
