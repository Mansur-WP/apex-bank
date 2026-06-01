"""
transfers/models.py — Transaction and ledger models.

Phase 7 adds a Double-Entry Ledger system via LedgerEntry.
"""

import uuid

from django.db import models
from django.db.models import Q


def generate_reference():
    """Return a unique transaction reference like 'TXN-3F8A1C4B9D2E7F01'."""
    return "TXN-" + uuid.uuid4().hex[:16].upper()


class Transaction(models.Model):
    """Immutable audit record of every completed transfer."""

    sender_account = models.ForeignKey(
        "bank_accounts.Account",
        on_delete=models.PROTECT,
        related_name="sent_transactions",
        verbose_name="Sender account",
    )
    receiver_account = models.ForeignKey(
        "bank_accounts.Account",
        on_delete=models.PROTECT,
        related_name="received_transactions",
        verbose_name="Receiver account",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Amount",
    )
    note = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Note",
    )
    reference = models.CharField(
        max_length=24,
        unique=True,
        default=generate_reference,
        editable=False,
        verbose_name="Reference",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Transferred at",
    )

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=0),
                name="transaction_amount_positive",
            ),
        ]

    def __str__(self):
        return (
            f"{self.reference} | "
            f"{self.sender_account.account_number} → "
            f"{self.receiver_account.account_number} | "
            f"₦{self.amount}"
        )


class LedgerEntry(models.Model):
    """Double-entry ledger movement for an account caused by a Transaction."""

    class EntryType(models.TextChoices):
        DEBIT = "DEBIT", "Debit"
        CREDIT = "CREDIT", "Credit"

    account = models.ForeignKey(
        "bank_accounts.Account",
        on_delete=models.PROTECT,
        related_name="ledger_entries",
        verbose_name="Account",
    )
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.PROTECT,
        related_name="ledger_entries",
        verbose_name="Transaction",
    )
    entry_type = models.CharField(
        max_length=6,
        choices=EntryType.choices,
        verbose_name="Entry type",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Amount",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Timestamp",
    )

    class Meta:
        verbose_name = "Ledger entry"
        verbose_name_plural = "Ledger entries"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=0),
                name="ledger_entry_amount_positive",
            ),
        ]

    def __str__(self):
        return (
            f"{self.entry_type} ₦{self.amount} "
            f"@ {self.account.account_number} "
            f"({self.transaction.reference})"
        )

