"""
apps.py — Application configuration for the bank_accounts app.

Why it exists:
    Django's AppConfig.ready() method is the correct place to connect signals.
    It runs exactly once, after all apps are fully loaded, avoiding circular
    import errors that can occur when signals are imported at module level.

What it does:
    Imports bank_accounts.signals inside ready() so that the @receiver
    decorator in signals.py is executed and the signal is registered with
    Django's signal dispatcher.

How it connects:
    - INSTALLED_APPS in settings.py references "bank_accounts.apps.BankAccountsConfig"
      (or simply "bank_accounts", Django finds the AppConfig automatically).
    - ready() fires after all models are loaded — safe to import signals here.
    - Without this import, the signal in signals.py is never registered and
      new users will not get bank accounts automatically.
"""

from django.apps import AppConfig


class BankAccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bank_accounts"
    verbose_name = "Bank Accounts"

    def ready(self):
        """
        Import signals module to register all signal receivers.
        Called once by Django after all apps are fully initialized.
        """
        import bank_accounts.signals  # noqa: F401
