from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Case
from .forms import CaseAssignmentForm

@login_required
def assign_case(request, case_id):
    case = get_object_or_404(Case, id=case_id)
    
    if request.method == 'POST':
        form = CaseAssignmentForm(request.POST, instance=case)
        if form.is_valid():
            case = form.save(commit=False)
            case.status = 'ASSIGNED' # Update status automatically
            case.save()
            return redirect('admin_dashboard') # Redirect to your dashboard
    else:
        form = CaseAssignmentForm(instance=case)
        
    return render(request, 'cases/assign_case.html', {'form': form, 'case': case})