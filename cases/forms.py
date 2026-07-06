from django import forms
from django.contrib.auth.models import Group
from .models import Case
from django.contrib.auth import get_user_model

User = get_user_model()


class CaseCreateForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = ['title', 'description', 'case_priority', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500', 'rows': 5}),
            'case_priority': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'image': forms.ClearableFileInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
        }


class CaseAssignmentForm(forms.ModelForm):
    technician = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name='Technician'),
        empty_label="Select a Technician",
        widget=forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
    )

    class Meta:
        model = Case
        fields = ['technician']


class CaseStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
        }
