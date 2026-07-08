from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Lab, Machine, IssueTemplate


def _is_admin(user):
    return user.is_superuser or user.groups.filter(name='Admin').exists()


@login_required
def lab_list(request):
    if not _is_admin(request.user):
        return HttpResponseForbidden("You do not have permission to access this page.")
    labs = Lab.objects.prefetch_related('machines').all()
    issues = IssueTemplate.objects.all()
    return render(request, 'labs/lab_list.html', {'labs': labs, 'issues': issues})


@login_required
def lab_create(request):
    if not _is_admin(request.user):
        return HttpResponseForbidden("You do not have permission.")
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        location = request.POST.get('location', '').strip()
        machine_count = int(request.POST.get('machine_count', 20))
        if name:
            lab = Lab.objects.create(name=name, location=location)
            for i in range(1, machine_count + 1):
                Machine.objects.create(
                    lab=lab,
                    name=f"{name}-PC{str(i).zfill(2)}",
                    status='HEALTHY'
                )
            messages.success(request, f'Lab {name} created with {machine_count} machines.')
    return redirect('lab_list')


@login_required
def lab_delete(request, lab_id):
    if not _is_admin(request.user):
        return HttpResponseForbidden("You do not have permission.")
    lab = get_object_or_404(Lab, id=lab_id)
    if request.method == 'POST':
        name = lab.name
        lab.delete()
        messages.success(request, f'Lab {name} deleted.')
    return redirect('lab_list')


@login_required
def machine_update(request, machine_id):
    if not _is_admin(request.user):
        return HttpResponseForbidden("You do not have permission.")
    machine = get_object_or_404(Machine, id=machine_id)
    if request.method == 'POST':
        status = request.POST.get('status', '')
        if status in dict(Machine.STATUS_CHOICES):
            machine.status = status
            machine.save()
            messages.success(request, f'{machine.name} status updated to {machine.get_status_display()}.')
    return redirect('lab_list')


@login_required
def issue_create(request):
    if not _is_admin(request.user):
        return HttpResponseForbidden("You do not have permission.")
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        priority = request.POST.get('default_priority', 'MEDIUM')
        if title:
            IssueTemplate.objects.create(title=title, default_priority=priority)
            messages.success(request, f'Issue "{title}" added with {priority} priority.')
    return redirect('lab_list')


@login_required
def issue_delete(request, issue_id):
    if not _is_admin(request.user):
        return HttpResponseForbidden("You do not have permission.")
    issue = get_object_or_404(IssueTemplate, id=issue_id)
    if request.method == 'POST':
        title = issue.title
        issue.delete()
        messages.success(request, f'Issue "{title}" deleted.')
    return redirect('lab_list')


@login_required
def issue_update_priority(request, issue_id):
    if not _is_admin(request.user):
        return HttpResponseForbidden("You do not have permission.")
    issue = get_object_or_404(IssueTemplate, id=issue_id)
    if request.method == 'POST':
        priority = request.POST.get('default_priority', 'MEDIUM')
        if priority in dict(IssueTemplate.PRIORITY_CHOICES):
            issue.default_priority = priority
            issue.save()
            messages.success(request, f'"{issue.title}" priority updated to {priority}.')
    return redirect('lab_list')
