"""transfers/services.py — Atomic transfer business logic.

Single source of truth for transfer validation and execution.
"""

from dataclasses import dataclass
from decimal import Decimal

from django.db import transaction

from bank_accounts.models import Account

from .models import Transaction


class TransferError(Exception):
    """Base class for transfer validation failures."""


class ReceiverNotFoundError(TransferError):
    pass


class SelfTransferError(TransferError):
    pass


class InsufficientFundsError(TransferError):
    def __init__(self, available: Decimal):
        self.available = available
        super().__init__("Insufficient funds")


@dataclass
class TransferResult:
    transaction: Transaction


def execute_transfer(
    sender_account: Account,
    to_account_number: str,
    amount: Decimal,
    note: str = "",
) -> TransferResult:
    """Move funds from sender to receiver inside one DB transaction.

    Locks both account rows in primary-key order to reduce deadlock risk.
    """
    if amount <= Decimal("0.00"):
        raise TransferError("Amount must be greater than zero.")

    try:
        receiver_account = Account.objects.get(
            account_number=to_account_number
        )
    except Account.DoesNotExist:
        raise ReceiverNotFoundError(
            "No account found with that number."
        )

    if receiver_account.pk == sender_account.pk:
        raise SelfTransferError(
            "You cannot transfer money to your own account."
        )

    if getattr(sender_account, "status", None) == "frozen":
        raise TransferError(
            "Frozen accounts cannot transfer money."
        )

    with transaction.atomic():
        locked_accounts = (
            Account.objects.select_for_update()
            .filter(pk__in=[sender_account.pk, receiver_account.pk])
            .order_by("pk")
        )
        locked_sender = locked_accounts.get(pk=sender_account.pk)
        locked_receiver = locked_accounts.get(pk=receiver_account.pk)

        if locked_sender.balance < amount:
            raise InsufficientFundsError(locked_sender.balance)

        locked_sender.balance -= amount
        locked_receiver.balance += amount
        locked_sender.save(update_fields=["balance", "updated_at"])
        locked_receiver.save(update_fields=["balance", "updated_at"])

        txn = Transaction.objects.create(
            sender_account=locked_sender,
            receiver_account=locked_receiver,
            amount=amount,
            note=note or "",
        )

    return TransferResult(transaction=txn)

