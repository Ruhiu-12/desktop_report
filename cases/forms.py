from django import forms
from django.contrib.auth.models import Group
from .models import Case
from django.contrib.auth import get_user_model

User = get_user_model()

class CaseAssignmentForm(forms.ModelForm):
    # Filter the technician field to show only users in the 'Technician' group
    technician = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name='Technician'),
        empty_label="Select a Technician"
    )

    class Meta:
        model = Case
        fields = ['technician']