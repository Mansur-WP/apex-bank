"""accounts/admin_actions.py

Staff-only write operations for the banking application.

Keeping these operations in a dedicated module helps ensure:
- permission checks happen consistently
- the business rule surface is centralized
- views stay thin
"""

from django.db import transaction

from bank_accounts.models import Account, AccountStatus


class AdminAccountActionError(Exception):
    """Base class for admin action failures."""


class AccountNotFound(AdminAccountActionError):
    pass


def freeze_account(*, acting_user, account_number: str) -> None:
    """Freeze an account.

    Business rules:
    - Only staff can freeze.
    """
    if not getattr(acting_user, "is_staff", False):
        raise PermissionError("Admin permission required.")

    try:
        account = Account.objects.select_for_update().get(
            account_number=account_number
        )
    except Account.DoesNotExist:
        raise AccountNotFound("Account not found.")

    if account.status != AccountStatus.FROZEN:
        with transaction.atomic():
            account.status = AccountStatus.FROZEN
            account.save(update_fields=["status"])


def unfreeze_account(*, acting_user, account_number: str) -> None:
    """Unfreeze an account.

    Business rules:
    - Only staff can unfreeze.
    """
    if not getattr(acting_user, "is_staff", False):
        raise PermissionError("Admin permission required.")

    try:
        account = Account.objects.select_for_update().get(
            account_number=account_number
        )
    except Account.DoesNotExist:
        raise AccountNotFound("Account not found.")

    if account.status != AccountStatus.ACTIVE:
        with transaction.atomic():
            account.status = AccountStatus.ACTIVE
            account.save(update_fields=["status"])

