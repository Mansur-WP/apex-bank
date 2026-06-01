"""bank_accounts/models.py

Bank account model for the banking simulator.

This app stores the financial side of the system (balances, account numbers)
while `accounts` owns identity (users).
"""

import random
import string
from decimal import Decimal

from django.conf import settings
from django.db import models


class AccountStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    FROZEN = "frozen", "Frozen"


def generate_account_number() -> str:
    """Generate a unique 10-digit numeric account number."""
    while True:
        number = "".join(
            random.choices(string.digits, k=10)
        )

        exists = Account.objects.filter(account_number=number).exists()
        if not exists:
            return number


class Account(models.Model):
    """A bank account belonging to one user."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="account",
        verbose_name="Account holder",
    )

    account_number = models.CharField(
        max_length=10,
        unique=True,
        editable=False,  # prevents accidental changes via admin or forms
        verbose_name="Account number",
    )

    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("10000.00"),
        verbose_name="Balance",
    )

    status = models.CharField(
        max_length=10,
        choices=AccountStatus.choices,
        default=AccountStatus.ACTIVE,
        verbose_name="Account status",
        db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Opened on")
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Last updated",
    )

    class Meta:
        verbose_name = "Bank Account"
        verbose_name_plural = "Bank Accounts"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Account {self.account_number} — {self.user.email}"

    def save(self, *args, **kwargs):
        """Auto-assign an account number on first save if missing."""
        if not self.account_number:
            self.account_number = generate_account_number()
        super().save(*args, **kwargs)

