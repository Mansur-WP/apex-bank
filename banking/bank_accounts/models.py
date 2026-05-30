"""
models.py — Bank account model for the banking simulator.

Why it exists:
    Separating account data from user data follows the single-responsibility
    principle. The `accounts` app owns identity (who you are); `bank_accounts`
    owns financial data (what you own). This clean boundary makes Phase 3
    (transfers) and Phase 4 (ledger) easy to add without touching user auth.

What it does:
    Defines the `Account` model — one row per user — storing:
        user            — the owner (OneToOne to CustomUser)
        account_number  — unique 10-digit identifier, auto-generated
        balance         — current balance (Decimal, 2 d.p., default 10 000.00)
        created_at      — timestamp set when the account row is first inserted
        updated_at      — timestamp auto-updated on every save

    Also provides generate_account_number(), a module-level helper that
    creates a random 10-digit string guaranteed to be unique in the DB.

How it connects:
    - signals.py listens for new CustomUser saves and calls Account.objects.create().
    - admin.py registers Account with the Django admin site.
    - accounts/views.py fetches account via request.user.account (reverse
      OneToOne accessor) to inject it into the dashboard context.
    - Phase 3 Transfer model will use ForeignKey(Account) for debit/credit.

Why OneToOne (not ForeignKey)?
    OneToOneField enforces exactly one account per user at the database level —
    the column has a UNIQUE constraint that PostgreSQL enforces atomically.
    A ForeignKey would allow multiple accounts per user, which is a Phase 3+
    concern (multi-account support). Using OneToOne now makes the constraint
    explicit and gives a clean reverse accessor: user.account.
    When Phase 3 introduces multi-account support, we can migrate this to a
    ForeignKey and add an `account_type` field without breaking existing code.
"""

import random
import string
from decimal import Decimal

from django.conf import settings
from django.db import models


def generate_account_number():
    """
    Generate a unique 10-digit numeric account number.

    How it works:
        1. Picks 10 random digits (0-9), joining them into a string.
           Leading zeros are preserved — this is an opaque identifier,
           not a number to be added or subtracted.
        2. Checks the database to confirm no existing account has that number.
        3. If a collision is found (astronomically rare with 10^10 possibilities
           and a small user base), it loops and tries again.
        4. Returns the first unique candidate found.

    Why not use a sequence / auto-increment?
        Sequential IDs leak information (account #1000001 tells an attacker
        there are ~1 million accounts). Random opaque numbers are safer.

    Why not use UUID?
        The spec requires exactly 10 digits for human-readable display.
    """
    while True:
        number = "".join(random.choices(string.digits, k=10))
        if not Account.objects.filter(account_number=number).exists():
            return number


class Account(models.Model):
    """
    A bank account belonging to one user.

    Fields:
        user           — OneToOne link to CustomUser; cascade-deletes the
                         account if the user is deleted (important for GDPR).
        account_number — 10-digit unique string; auto-generated on creation,
                         never editable after that.
        balance        — current balance; max_digits=12 supports balances up
                         to 9 999 999 999.99 (ten billion minus one cent).
                         decimal_places=2 matches standard currency precision.
        created_at     — immutable creation timestamp (auto_now_add=True).
        updated_at     — mutable last-modified timestamp (auto_now=True);
                         updated automatically by Django on every .save() call.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="account",
        verbose_name="Account holder",
    )
    account_number = models.CharField(
        max_length=10,
        unique=True,
        editable=False,      # prevents accidental changes via admin or forms
        verbose_name="Account number",
    )
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("10000.00"),
        verbose_name="Balance",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Opened on")
    updated_at = models.DateTimeField(auto_now=True,     verbose_name="Last updated")

    class Meta:
        verbose_name = "Bank Account"
        verbose_name_plural = "Bank Accounts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Account {self.account_number} — {self.user.email}"

    def save(self, *args, **kwargs):
        """
        Auto-assign an account number on first save if none has been set.
        Calling generate_account_number() here (rather than as a field default)
        means the uniqueness check hits the DB, which field defaults cannot do.
        """
        if not self.account_number:
            self.account_number = generate_account_number()
        super().save(*args, **kwargs)
