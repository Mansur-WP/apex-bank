"""
apps.py — Application configuration for the accounts app.

Why it exists:
    Django uses AppConfig subclasses to configure each installed application.
    This is where app-level metadata and startup signals would be registered.

What it does:
    Declares the `accounts` app with its full dotted path and a human-
    readable name shown in the Django admin.

How it connects:
    Referenced by INSTALLED_APPS in settings.py. Django's app registry
    discovers this class automatically when the app is installed.
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
    verbose_name = "User Accounts"
