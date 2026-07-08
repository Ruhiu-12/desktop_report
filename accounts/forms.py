from django import forms
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['identifier', 'email', 'first_name', 'last_name']
        widgets = {
            'identifier': forms.TextInput(attrs={'placeholder': 'e.g. i231/g/8401/23'}),
            'email': forms.EmailInput(attrs={'placeholder': 'user@example.com'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last name'}),
        }

    def clean_identifier(self):
        identifier = self.cleaned_data.get('identifier', '').strip()
        if not identifier:
            raise forms.ValidationError("Employee/Admin number is required.")
        if len(identifier) < 3:
            raise forms.ValidationError("Identifier must be at least 3 characters.")
        import re
        if not re.match(r'^[A-Za-z0-9/\-_]+$', identifier):
            raise forms.ValidationError("Identifier can only contain letters, numbers, slashes, dashes, or underscores.")
        return identifier.upper()

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise forms.ValidationError("Email is required.")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', '').strip()
        if first_name and not first_name.isalpha():
            raise forms.ValidationError("First name must contain only letters.")
        return first_name.title() if first_name else first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name', '').strip()
        if last_name and not last_name.isalpha():
            raise forms.ValidationError("Last name must contain only letters.")
        return last_name.title() if last_name else last_name

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user