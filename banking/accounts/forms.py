"""
forms.py — Registration and login forms for the accounts app.

Why it exists:
    Forms handle user input validation in Django's MVT pattern. Keeping
    them separate from views keeps each file focused on one concern.

What it does:
    - RegistrationForm: validates new user sign-up data, including
      password confirmation, and creates a CustomUser on save().
    - LoginForm: a thin wrapper around Django's AuthenticationForm
      so we can render it with Bootstrap classes and email labels.

How it connects:
    - RegistrationForm is used by accounts.views.RegisterView.
    - LoginForm is used by accounts.views.CustomLoginView.
    - Both forms render inside their respective templates using
      Django's {{ form.as_p }} or field-by-field rendering.
"""

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser


class RegistrationForm(forms.ModelForm):
    """
    Form for creating a new CustomUser account.

    Extra fields beyond the model:
        password1  — the desired password (not stored as-is)
        password2  — confirmation; must match password1
    """

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Create a password",
        }),
    )
    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Repeat the password",
        }),
    )

    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "email")
        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "First name",
            }),
            "last_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Last name",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Email address",
            }),
        }

    def clean_password2(self):
        """Ensure both password fields match before saving."""
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return p2

    def save(self, commit=True):
        """
        Save a new user with a hashed password.
        Never stores the raw password — delegates to set_password().
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    """
    Login form using email as the username field.

    Inherits all validation logic from Django's AuthenticationForm
    (brute-force protection, inactive user handling, etc.).
    We only override the widget attrs to apply Bootstrap classes.
    """

    username = forms.EmailField(
        label="Email address",
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Email address",
            "autofocus": True,
        }),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Password",
        }),
    )
