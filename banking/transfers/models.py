"""
transfers/models.py — Transaction model for Phase 3.

Why it exists:
    Every successful money transfer must leave a permanent, immutable record.
    This model is that record — one row per completed transfer. It is never
    edited after creation; the audit trail must be append-only.

What it stores:
    sender_account   — the account that was debited
    receiver_account — the account that was credited
    amount           — the exact amount moved (Decimal, 2 d.p.)
    reference        — human-readable unique ID (e.g. "TXN-3F8A1C...")
    created_at       — timestamp when the transfer completed

How money conservation is guaranteed:
    The transfer view uses transaction.atomic. Inside a single database
    transaction:
        1. sender.balance   -= amount  → debit
        2. receiver.balance += amount  → credit
        3. Transaction.objects.create(...)  → record
    If any step fails (DB error, exception), the entire transaction rolls
    back. Balances return to their pre-transfer state and no record is
    written. It is impossible for money to disappear or be created:
    every unit subtracted from one balance is added to exactly one other.

    select_for_update() in the view locks both account rows during the
    transaction, preventing concurrent transfers from reading stale balances.

Reference format:
    "TXN-" + first 16 chars of a UUID4 hex string, uppercased.
    e.g. "TXN-3F8A1C4B9D2E7F01"
    Unique at the DB level (unique=True on the field).
"""

import uuid

from django.db import models


def generate_reference():
    """Return a unique transaction reference string like 'TXN-3F8A1C4B9D2E7F01'."""
    return "TXN-" + uuid.uuid4().hex[:16].upper()


class Transaction(models.Model):
    """
    An immutable record of a completed money transfer.

    Fields:
        sender_account   — FK to bank_accounts.Account; the debited account.
                           on_delete=PROTECT prevents deleting an account that
                           has transfer history (financial records must persist).
        receiver_account — FK to bank_accounts.Account; the credited account.
                           Same protection.
        amount           — amount transferred; always > 0 (enforced in the view).
                           max_digits=12 matches Account.balance precision.
        reference        — unique human-readable ID; never reused.
        created_at       — immutable timestamp (auto_now_add=True).
    """

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
