from django import forms
from cases.models import Report

ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB


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

    def clean_findings(self):
        findings = self.cleaned_data.get('findings', '').strip()
        if not findings:
            raise forms.ValidationError("Findings are required.")
        if len(findings) < 10:
            raise forms.ValidationError("Findings must be at least 10 characters.")
        return findings

    def clean_solution_provided(self):
        solution = self.cleaned_data.get('solution_provided', '').strip()
        if not solution:
            raise forms.ValidationError("Solution description is required.")
        if len(solution) < 10:
            raise forms.ValidationError("Solution must be at least 10 characters.")
        return solution

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.content_type not in ALLOWED_IMAGE_TYPES:
                raise forms.ValidationError("Only JPEG, PNG, GIF, and WebP images are allowed.")
            if image.size > MAX_IMAGE_SIZE:
                raise forms.ValidationError("Image must be less than 5MB.")
        return image
