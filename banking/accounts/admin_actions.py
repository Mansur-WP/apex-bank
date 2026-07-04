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
    """Freeze a bank account.

    Canonical frozen state is stored on `bank_accounts.Account.status`.
    For backward compatibility, we mirror the state into
    `accounts.CustomUser.is_frozen`.
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

    if account.status != AccountStatus.FROZEN:
        with transaction.atomic():
            account.status = AccountStatus.FROZEN
            account.save(update_fields=["status"])

            if not account.user.is_frozen:
                account.user.is_frozen = True
                account.user.save(update_fields=["is_frozen"])


def unfreeze_account(*, acting_user, account_number: str) -> None:
    """Unfreeze a bank account.

    Canonical frozen state is stored on `bank_accounts.Account.status`.
    For backward compatibility, we mirror the state into
    `accounts.CustomUser.is_frozen`.
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

    if account.status != AccountStatus.ACTIVE:
        with transaction.atomic():
            account.status = AccountStatus.ACTIVE
            account.save(update_fields=["status"])

            if account.user.is_frozen:
                account.user.is_frozen = False
                account.user.save(update_fields=["is_frozen"])

