from django import forms
from django.contrib.auth.models import Group
from .models import Case
from django.contrib.auth import get_user_model

User = get_user_model()

ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB


class CaseCreateForm(forms.ModelForm):
    class Meta:
        model = Case
        fields = ['title', 'description', 'asset_tag', 'case_priority', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500', 'placeholder': 'Brief title of the issue'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500', 'rows': 5, 'placeholder': 'Describe the issue in detail...'}),
            'case_priority': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
            'image': forms.ClearableFileInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['case_priority'].initial = 'MEDIUM'
        self.fields['case_priority'].required = False

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise forms.ValidationError("Title is required.")
        if len(title) < 5:
            raise forms.ValidationError("Title must be at least 5 characters.")
        if len(title) > 200:
            raise forms.ValidationError("Title must not exceed 200 characters.")
        return title

    def clean_description(self):
        description = self.cleaned_data.get('description', '').strip()
        if not description:
            raise forms.ValidationError("Description is required.")
        if len(description) < 10:
            raise forms.ValidationError("Description must be at least 10 characters.")
        return description

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.content_type not in ALLOWED_IMAGE_TYPES:
                raise forms.ValidationError("Only JPEG, PNG, GIF, and WebP images are allowed.")
            if image.size > MAX_IMAGE_SIZE:
                raise forms.ValidationError("Image must be less than 5MB.")
        return image


class CaseAssignmentForm(forms.ModelForm):
    technician = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name='Technician'),
        empty_label="Select a Technician",
        widget=forms.Select(attrs={'class': 'input'}),
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
