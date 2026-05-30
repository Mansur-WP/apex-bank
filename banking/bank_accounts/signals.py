"""
signals.py — Django signals for automatic bank account creation.

Why it exists:
    The business rule "every registered user automatically gets a bank account"
    should not live in the registration view. If a staff member creates a user
    via the admin, or a future API endpoint creates one, the account must still
    be created. A signal fires for every CustomUser save, regardless of where
    the save originated — it is the single, authoritative place for this rule.

What it does:
    Listens to the post_save signal on CustomUser. When a brand-new user is
    saved (created=True), it creates one Account row for that user.

How the signal works — step by step:
    1. A CustomUser is saved anywhere in the codebase (RegisterView, admin,
       management command, test factory — doesn't matter).
    2. Django fires the post_save signal, passing the sender class, the
       saved instance, and a `created` boolean.
    3. Our receiver checks `if created` — we only want one account per user,
       created at registration time, not on every subsequent profile update.
    4. Account.objects.create(user=instance) is called. Account.save()
       auto-generates the account number and sets balance=10000.00.
    5. The account is now in the database, linked to the user by OneToOne.

How it connects:
    - This module is imported in BankAccountsConfig.ready() (apps.py), which
      is called once when Django finishes loading all apps. This is the
      Django-recommended way to register signals — importing signals at
      module level (e.g., in models.py) can cause circular import problems.
    - bank_accounts/models.py defines Account, which this signal creates.
    - accounts/models.py defines CustomUser, which this signal listens to.
"""

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Account


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_account_for_new_user(sender, instance, created, **kwargs):
    """
    Signal receiver: create one Account whenever a new CustomUser is saved.

    Parameters:
        sender   — the model class that sent the signal (CustomUser)
        instance — the actual CustomUser object that was just saved
        created  — True if this is an INSERT (new row), False if UPDATE
        **kwargs — additional signal arguments (we don't need them)
    """
    if created:
        Account.objects.create(user=instance)
