"""
transfers/models.py — Transaction model for Phase 3.

Immutable audit record of every completed transfer.
"""

import uuid

from django.db import models


def generate_reference():
    """Return a unique transaction reference like 'TXN-3F8A1C4B9D2E7F01'."""
    return "TXN-" + uuid.uuid4().hex[:16].upper()


class Transaction(models.Model):
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

    def __str__(self):
        return (
            f"{self.reference} | "
            f"{self.sender_account.account_number} → "
            f"{self.receiver_account.account_number} | "
            f"${self.amount}"
        )
