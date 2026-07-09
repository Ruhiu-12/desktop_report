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
    if user.is_superuser or user.groups.filter(name='Admin').exists():
        pass  # See all
    elif user.groups.filter(name='Technician').exists():
        queryset = queryset.filter(technician=user)
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
    if not (user.is_superuser or user.groups.filter(name='Admin').exists()
            or case.created_by == user or case.technician == user):
        return HttpResponseForbidden("You do not have permission to view this case.")

    is_admin = user.is_superuser or user.groups.filter(name='Admin').exists()

    context = {
        'case': case,
        'audit_logs': audit_logs,
        'notes': notes,
        'status_choices': Case.STATUS_CHOICES,
        'is_admin': is_admin,
    }
    return render(request, 'cases/case_detail.html', context)


@login_required
def case_add_note(request, case_id):
    case = get_object_or_404(Case, id=case_id)
    user = request.user

    if not (user.is_superuser or user.groups.filter(name='Admin').exists()
            or case.created_by == user or case.technician == user):
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


def case_create(request):
    from labs.models import IssueTemplate, Machine
    issue_templates = IssueTemplate.objects.filter(is_active=True)

    if request.method == 'POST':
        form = CaseCreateForm(request.POST, request.FILES)
        if form.is_valid():
            case = form.save(commit=False)
            if request.user.is_authenticated:
                case.created_by = request.user
            else:
                case.created_by = None
            # Get asset_tag from POST data (not in form fields)
            asset_tag = request.POST.get('asset_tag', '').strip()
            if asset_tag:
                case.asset_tag = asset_tag
            case.save()

            # Update machine status if asset_tag matches a machine
            if asset_tag:
                try:
                    machine = Machine.objects.get(name=asset_tag)
                    if machine.status == 'HEALTHY':
                        machine.status = 'FLAGGED'
                        machine.save()
                except Machine.DoesNotExist:
                    pass

            CaseAuditLog.objects.create(
                case=case,
                action='Case created',
                changed_by=request.user if request.user.is_authenticated else None,
            )
            messages.success(request, 'Your issue has been submitted. Thank you!')
            if request.user.is_authenticated:
                return redirect('case_detail', case_id=case.id)
            else:
                return redirect('home')
    else:
        form = CaseCreateForm()

    return render(request, 'cases/case_create_public.html', {'form': form, 'issue_templates': issue_templates})


@login_required
def case_review(request, case_id):
    case = get_object_or_404(Case.objects.select_related('created_by', 'technician'), id=case_id)
    user = request.user
    is_admin = user.is_superuser or user.groups.filter(name='Admin').exists()

    if not is_admin:
        return HttpResponseForbidden("Only admins can review cases.")

    report = getattr(case, 'report', None)
    audit_logs = case.audit_logs.select_related('changed_by').all()
    notes = case.notes.select_related('author').all()

    context = {
        'case': case,
        'report': report,
        'audit_logs': audit_logs,
        'notes': notes,
        'is_admin': is_admin,
    }
    return render(request, 'cases/case_review.html', context)


@login_required
def case_review_add_note(request, case_id):
    case = get_object_or_404(Case, id=case_id)
    user = request.user

    if not (user.is_superuser or user.groups.filter(name='Admin').exists()):
        return HttpResponseForbidden("Only admins can add review notes.")

    if request.method == 'POST':
        work_items = []
        if request.POST.get('work_diagnosed'):
            work_items.append('Diagnosed the issue')
        if request.POST.get('work_identified'):
            work_items.append('Identified root cause')
        if request.POST.get('work_repaired'):
            work_items.append('Repaired / replaced parts')
        if request.POST.get('work_tested'):
            work_items.append('Tested and verified fix')
        if request.POST.get('work_documented'):
            work_items.append('Documented with evidence')

        admin_note = request.POST.get('admin_note', '').strip()

        note_parts = []
        if work_items:
            note_parts.append('Work completed: ' + ', '.join(work_items))
        if admin_note:
            note_parts.append('Admin note: ' + admin_note)

        if note_parts:
            note = CaseNote.objects.create(
                case=case,
                author=user,
                content=' | '.join(note_parts),
            )
            CaseAuditLog.objects.create(
                case=case,
                action='Admin review notes added',
                changed_by=user,
                related_note=note,
            )
            messages.success(request, 'Review notes saved.')

    return redirect('case_review', case_id=case.id)


@login_required
def case_delete(request, case_id):
    case = get_object_or_404(Case, id=case_id)
    user = request.user

    if not (user.is_superuser or user.groups.filter(name='Admin').exists()):
        return HttpResponseForbidden("Only admins can delete cases.")

    if request.method == 'POST':
        title = case.title
        case.delete()
        messages.success(request, f'Case "{title}" deleted.')
        return redirect('case_list')

    return redirect('case_detail', case_id=case.id)


@login_required
def case_assign(request, case_id):
    case = get_object_or_404(Case, id=case_id)
    user = request.user

    if not (user.is_superuser or user.groups.filter(name='Admin').exists()):
        return HttpResponseForbidden("You do not have permission to assign cases.")

    if request.method == 'POST':
        form = CaseAssignmentForm(request.POST, instance=case)
        if form.is_valid():
            old_tech = case.technician
            case = form.save(commit=False)
            case.status = 'ASSIGNED'
            case.save()

            # Update machine status to IN_REPAIR when assigned
            if case.asset_tag:
                from labs.models import Machine
                try:
                    machine = Machine.objects.get(name=case.asset_tag)
                    machine.status = 'IN_REPAIR'
                    machine.save()
                except Machine.DoesNotExist:
                    pass

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
    from labs.models import Machine
    case = get_object_or_404(Case, id=case_id)
    user = request.user

    if not (user.is_superuser or user.groups.filter(name='Admin').exists()
            or case.technician == user):
        return HttpResponseForbidden("You do not have permission to update this case.")

    # Define allowed status transitions per role
    if user.is_superuser or user.groups.filter(name='Admin').exists():
        allowed_statuses = ['ASSIGNED', 'IN_PROGRESS', 'WAITING_REPORT', 'PENDING_REVIEW', 'CLOSED']
    elif case.technician == user:
        allowed_statuses = ['IN_PROGRESS', 'WAITING_REPORT', 'PENDING_REVIEW']
    else:
        allowed_statuses = []

    if request.method == 'POST':
        new_status = request.POST.get('status', '')
        if new_status in allowed_statuses:
            old_status = case.status
            case.status = new_status
            case.save()

            # Update machine status based on case status
            if case.asset_tag:
                try:
                    machine = Machine.objects.get(name=case.asset_tag)
                    if new_status == 'IN_PROGRESS':
                        machine.status = 'IN_REPAIR'
                        machine.save()
                    elif new_status == 'CLOSED':
                        machine.status = 'HEALTHY'
                        machine.save()
                    elif new_status == 'WAITING_REPORT':
                        machine.status = 'FLAGGED'
                        machine.save()
                except Machine.DoesNotExist:
                    pass

            CaseAuditLog.objects.create(
                case=case,
                action=f'Status changed from {old_status} to {new_status}',
                changed_by=request.user,
            )
            messages.success(request, f'Case status updated to {case.get_status_display()}.')
        else:
            messages.error(request, 'Invalid status transition.')

    return redirect('case_detail', case_id=case.id)
