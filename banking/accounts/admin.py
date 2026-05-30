"""
admin.py — Django admin registration for the custom user model.

Why it exists:
    Django's admin site does not automatically know about CustomUser.
    We must explicitly register it with a custom ModelAdmin so the admin
    panel renders correctly (custom fields, proper fieldsets, password widget).

What it does:
    - Registers CustomUser with the admin site.
    - Configures list_display so the admin table shows useful columns.
    - Uses UserChangeForm and UserCreationForm (adapted for our model) to
      render the correct password widget in the admin.

How it connects:
    Depends on accounts.models.CustomUser. Referenced by Django's admin
    autodiscovery when the server starts.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Admin configuration for CustomUser.

    Extends Django's built-in UserAdmin to handle our email-based model.
    """
    model = CustomUser

    # Columns shown in the user list view
    list_display = ("email", "first_name", "last_name", "is_staff", "is_active", "date_joined")
    list_filter = ("is_staff", "is_active")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("-date_joined",)

    # Fieldsets for the user *edit* form in admin
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    # Fieldsets for the user *add* form in admin
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "password1", "password2", "is_staff", "is_active"),
        }),
    )
