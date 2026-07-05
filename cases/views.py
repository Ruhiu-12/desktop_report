from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden
from .models import Case, CaseAuditLog, CaseNote
from .forms import CaseAssignmentForm, CaseCreateForm, CaseStatusUpdateForm

User = get_user_model()


@login_required
def case_list(request):
    queryset = Case.objects.select_related('created_by', 'technician')
    user = request.user

    # Role-based filtering
    if user.is_superuser or user.groups.filter(name='admin').exists():
        pass  # See all
    elif user.groups.filter(name='technician').exists():
        queryset = queryset.filter(technician=user)
    elif user.groups.filter(name='analyst').exists():
        queryset = queryset.filter(status='PENDING_REVIEW')
    else:
        queryset = queryset.filter(created_by=user)

    # Search filter
    search_query = request.GET.get('search', '').strip()
    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )

    # Status filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        queryset = queryset.filter(status=status_filter)

    # Priority filter
    priority_filter = request.GET.get('priority', '')
    if priority_filter:
        queryset = queryset.filter(case_priority=priority_filter)

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'status_choices': Case.STATUS_CHOICES,
        'priority_choices': Case.PRIORITY_CHOICES,
    }
    return render(request, 'cases/case_list.html', context)


@login_required
def case_detail(request, case_id):
    case = get_object_or_404(Case.objects.select_related('created_by', 'technician'), id=case_id)
    audit_logs = case.audit_logs.select_related('changed_by').all()
    notes = case.notes.select_related('author').all()

    user = request.user
    if not (user.is_superuser or user.groups.filter(name='admin').exists()
            or case.created_by == user or case.technician == user
            or user.groups.filter(name='analyst').exists()):
        return HttpResponseForbidden("You do not have permission to view this case.")

    context = {
        'case': case,
        'audit_logs': audit_logs,
        'notes': notes,
        'status_choices': Case.STATUS_CHOICES,
    }
    return render(request, 'cases/case_detail.html', context)


@login_required
def case_add_note(request, case_id):
    case = get_object_or_404(Case, id=case_id)
    user = request.user

    if not (user.is_superuser or user.groups.filter(name='admin').exists()
            or case.created_by == user or case.technician == user
            or user.groups.filter(name='analyst').exists()):
        return HttpResponseForbidden("You do not have permission to add notes to this case.")

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            CaseNote.objects.create(
                case=case,
                author=user,
                content=content,
            )
            CaseAuditLog.objects.create(
                case=case,
                action=f'Note added by {user.identifier}',
                changed_by=user,
            )
            messages.success(request, 'Note added.')

    return redirect('case_detail', case_id=case.id)


@login_required
def case_create(request):
    if request.method == 'POST':
        form = CaseCreateForm(request.POST, request.FILES)
        if form.is_valid():
            case = form.save(commit=False)
            case.created_by = request.user
            case.save()
            CaseAuditLog.objects.create(
                case=case,
                action='Case created',
                changed_by=request.user,
            )
            messages.success(request, 'Case created successfully.')
            return redirect('case_detail', case_id=case.id)
    else:
        form = CaseCreateForm()

    return render(request, 'cases/case_create.html', {'form': form})


@login_required
def case_assign(request, case_id):
    case = get_object_or_404(Case, id=case_id)
    user = request.user

    if not (user.is_superuser or user.groups.filter(name='admin').exists()):
        return HttpResponseForbidden("You do not have permission to assign cases.")

    if request.method == 'POST':
        form = CaseAssignmentForm(request.POST, instance=case)
        if form.is_valid():
            old_tech = case.technician
            case = form.save(commit=False)
            case.status = 'ASSIGNED'
            case.save()
            CaseAuditLog.objects.create(
                case=case,
                action=f'Case assigned to {case.technician}',
                changed_by=request.user,
            )
            messages.success(request, f'Case assigned to {case.technician}.')
            return redirect('case_detail', case_id=case.id)
    else:
        form = CaseAssignmentForm(instance=case)

    return render(request, 'cases/case_assign.html', {'form': form, 'case': case})


@login_required
def case_update_status(request, case_id):
    case = get_object_or_404(Case, id=case_id)
    user = request.user

    if not (user.is_superuser or user.groups.filter(name='admin').exists()
            or case.technician == user):
        return HttpResponseForbidden("You do not have permission to update this case.")

    # Define allowed status transitions per role
    if user.is_superuser or user.groups.filter(name='admin').exists():
        allowed_statuses = ['IN_PROGRESS', 'PENDING_REVIEW', 'CLOSED']
    elif case.technician == user:
        allowed_statuses = ['IN_PROGRESS', 'PENDING_REVIEW']
    else:
        allowed_statuses = []

    if request.method == 'POST':
        new_status = request.POST.get('status', '')
        if new_status in allowed_statuses:
            old_status = case.status
            case.status = new_status
            case.save()
            CaseAuditLog.objects.create(
                case=case,
                action=f'Status changed from {old_status} to {new_status}',
                changed_by=request.user,
            )
            messages.success(request, f'Case status updated to {case.get_status_display()}.')
        else:
            messages.error(request, 'Invalid status transition.')

    return redirect('case_detail', case_id=case.id)
