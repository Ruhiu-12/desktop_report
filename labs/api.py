from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Lab, Machine, IssueTemplate


def lab_machines_api(request):
    """Return all labs and their machines as JSON for the frontend."""
    labs = Lab.objects.prefetch_related('machines').all()
    data = []
    for lab in labs:
        machines = []
        for m in lab.machines.all():
            machines.append({
                'name': m.name,
                'status': m.status.lower().replace('_', ''),
                'row': m.grid_row,
                'col': m.grid_col,
            })
        data.append({
            'name': lab.name,
            'location': lab.location,
            'machine_count': lab.machines.count(),
            'grid_columns': lab.grid_columns,
            'machines': machines,
        })
    return JsonResponse({'labs': data})


@login_required
def issue_templates_api(request):
    """Return issue templates as JSON, with optional search filter."""
    search = request.GET.get('search', '').strip()
    queryset = IssueTemplate.objects.filter(is_active=True)

    if search:
        queryset = queryset.filter(title__icontains=search)

    # Limit to 20 results
    issues = queryset[:20]

    data = []
    for issue in issues:
        data.append({
            'id': issue.id,
            'title': issue.title,
            'priority': issue.default_priority,
        })

    return JsonResponse({'issues': data})
