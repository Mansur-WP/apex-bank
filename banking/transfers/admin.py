"""
transfers/admin.py — Register Transaction with the Django admin site.
"""

from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display  = ("reference", "sender_account", "receiver_account", "amount", "created_at")
    list_filter   = ("created_at",)
    search_fields = ("reference", "sender_account__account_number", "receiver_account__account_number")
    readonly_fields = ("reference", "sender_account", "receiver_account", "amount", "created_at")
    ordering      = ("-created_at",)

    def has_add_permission(self, request):
        return False  # Transactions must only be created via the transfer flow

    def has_change_permission(self, request, obj=None):
        return False  # Transactions are immutable audit records
