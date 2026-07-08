from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden
from logs.models import ActivityLog

User = get_user_model()

ADMIN_GROUPS = ['Admin']


def _is_admin(user):
    return user.is_superuser or user.groups.filter(name__in=ADMIN_GROUPS).exists()


@login_required
def user_list(request):
    if not _is_admin(request.user):
        return HttpResponseForbidden("You do not have permission to access this page.")

    queryset = User.objects.all().order_by('-date_joined')

    search_query = request.GET.get('search', '').strip()
    if search_query:
        queryset = queryset.filter(
            Q(identifier__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    role_filter = request.GET.get('role', '')
    if role_filter:
        queryset = queryset.filter(groups__name=role_filter)

    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        queryset = queryset.filter(is_active=True)
    elif status_filter == 'inactive':
        queryset = queryset.filter(is_active=False)

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    roles = Group.objects.values_list('name', flat=True).order_by('name')

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'roles': roles,
    }
    return render(request, 'users/user_list.html', context)


@login_required
def user_detail(request, user_id):
    if not _is_admin(request.user):
        return HttpResponseForbidden("You do not have permission to access this page.")

    target_user = get_object_or_404(User, id=user_id)

    cases_created = target_user.reported_cases.select_related('technician').order_by('-created_at')[:10]
    cases_assigned = target_user.assigned_cases.select_related('created_by').order_by('-created_at')[:10]

    user_groups = target_user.groups.values_list('name', flat=True)
    all_groups = Group.objects.exclude(name='Analyst').values_list('name', flat=True).order_by('name')

    context = {
        'target_user': target_user,
        'cases_created': cases_created,
        'cases_assigned': cases_assigned,
        'user_groups': list(user_groups),
        'all_groups': all_groups,
    }
    return render(request, 'users/user_detail.html', context)


@login_required
def user_update_role(request, user_id):
    if not _is_admin(request.user):
        return HttpResponseForbidden("You do not have permission to access this page.")

    target_user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        role = request.POST.get('role', '')
        all_roles = ['Admin', 'Technician', 'Student']

        if role in all_roles:
            old_roles = list(target_user.groups.values_list('name', flat=True))
            target_user.groups.clear()
            group, _ = Group.objects.get_or_create(name=role)
            target_user.groups.add(group)
            ActivityLog.objects.create(
                user=request.user,
                action='USER_UPDATE_ROLE',
                description=f'Changed {target_user.identifier} role from {", ".join(old_roles) or "None"} to {role}'
            )
            messages.success(request, f"Role for {target_user.identifier} changed to {role}.")
        else:
            messages.error(request, "Invalid role selected.")

    return redirect('user_detail', user_id=user_id)


@login_required
def user_delete(request, user_id):
    if not _is_admin(request.user):
        return HttpResponseForbidden("You do not have permission to access this page.")

    target_user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        if target_user == request.user:
            messages.error(request, "You cannot delete your own account.")
            return redirect('user_detail', user_id=user_id)

        identifier = target_user.identifier
        ActivityLog.objects.create(
            user=request.user,
            action='USER_DELETE',
            description=f'Deleted user {identifier}'
        )
        target_user.delete()
        messages.success(request, f"User {identifier} has been deleted.")
        return redirect('user_list')

    return redirect('user_detail', user_id=user_id)
