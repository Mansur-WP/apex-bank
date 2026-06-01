"""accounts/admin_actions.py

Staff-only write operations for the banking application.

Keeping these operations in a dedicated module helps ensure:
- permission checks happen consistently
- the business rule surface is centralized
- views stay thin
"""

from django.db import transaction

from bank_accounts.models import Account


class AdminAccountActionError(Exception):
    """Base class for admin action failures."""


class AccountNotFound(AdminAccountActionError):
    pass


def freeze_account(*, acting_user, account_number: str) -> None:
    """Freeze a user account (identity-level freezing).

    Requirements:
    - Only staff can freeze.
    - Freezing uses CustomUser.is_frozen (never Django's is_active).
    """
    if not getattr(acting_user, "is_staff", False):
        raise PermissionError("Admin permission required.")

    try:
        account = (
            Account.objects.select_for_update()
            .select_related("user")
            .get(account_number=account_number)
        )
    except Account.DoesNotExist as exc:
        raise AccountNotFound("Account not found.") from exc

    if not account.user.is_frozen:
        with transaction.atomic():
            account.user.is_frozen = True
            account.user.save(update_fields=["is_frozen"])


def unfreeze_account(*, acting_user, account_number: str) -> None:
    """Unfreeze a user account (identity-level freezing).

    Requirements:
    - Only staff can unfreeze.
    - Unfreezing uses CustomUser.is_frozen (never Django's is_active).
    """
    if not getattr(acting_user, "is_staff", False):
        raise PermissionError("Admin permission required.")

    try:
        account = (
            Account.objects.select_for_update()
            .select_related("user")
            .get(account_number=account_number)
        )
    except Account.DoesNotExist as exc:
        raise AccountNotFound("Account not found.") from exc

    if account.user.is_frozen:
        with transaction.atomic():
            account.user.is_frozen = False
            account.user.save(update_fields=["is_frozen"])

