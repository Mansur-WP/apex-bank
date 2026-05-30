"""
admin.py — Django admin registration for the Account model.

Why it exists:
    Django does not automatically surface models in the admin panel.
    We register Account here with a custom ModelAdmin so staff can view
    account numbers, balances, owners, and timestamps at a glance.

What it does:
    - Registers Account with the admin site.
    - Configures list_display to show the most useful columns.
    - Makes account_number searchable so staff can look up a specific account.
    - Marks balance as the only editable financial field (account_number is
      set editable=False on the model, so it is read-only everywhere).
    - Adds an inline to CustomUserAdmin so every user record shows their
      linked account inside the same admin page.

How it connects:
    - Imports Account from bank_accounts.models.
    - Imports CustomUserAdmin from accounts.admin so we can attach the inline.
    - Django's admin autodiscovery picks this file up at startup.
"""

from django.contrib import admin

from .models import Account


class AccountInline(admin.StackedInline):
    """
    Inline that appears inside the CustomUser admin page.

    Why StackedInline (not TabularInline)?
        There is only ever one account per user (OneToOne), so the extra
        row-per-field layout of StackedInline is more readable than a
        wide table row.
    """
    model = Account
    extra = 0           # don't show blank extra forms
    readonly_fields = ("account_number", "created_at", "updated_at")
    fields = ("account_number", "balance", "created_at", "updated_at")
    can_delete = False  # accounts should not be deleted from the user edit page


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    """
    Standalone admin view for the Account model.
    """
    list_display = ("account_number", "user_email", "balance", "created_at", "updated_at")
    list_filter  = ("created_at",)
    search_fields = ("account_number", "user__email", "user__first_name", "user__last_name")
    readonly_fields = ("account_number", "created_at", "updated_at")
    ordering = ("-created_at",)

    @admin.display(description="User email", ordering="user__email")
    def user_email(self, obj):
        return obj.user.email


# ── Attach the inline to the existing CustomUserAdmin ─────────────────────────
# We import and patch here rather than in accounts/admin.py to avoid a circular
# dependency: accounts should not import from bank_accounts.
from accounts.admin import CustomUserAdmin  # noqa: E402

CustomUserAdmin.inlines = [AccountInline]
