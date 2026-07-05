from django import forms
from cases.models import Report


class ReportCreateForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['findings', 'solution_provided', 'image']
        widgets = {
            'findings': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 6,
                'placeholder': 'Describe your findings...'
            }),
            'solution_provided': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': 6,
                'placeholder': 'Describe the solution provided...'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            }),
        }
