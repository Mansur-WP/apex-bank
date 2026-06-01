"""
transfers/urls.py — URL patterns for the transfers app.
Mounted at /transfers/ in banking_project/urls.py.
"""

from django.urls import path

from .views import (
    AccountStatementView,
    TransactionDetailView,
    TransactionHistoryView,
    TransferView,
    VerifyRecipientView,
)

from .views_ledger import LedgerAuditView, MyLedgerEntriesView



urlpatterns = [
    path("", TransferView.as_view(), name="transfer"),
    path("verify-recipient/", VerifyRecipientView.as_view(), name="verify_recipient"),
    path("history/", TransactionHistoryView.as_view(), name="history"),
    path("statement/", AccountStatementView.as_view(), name="statement"),
    path(
        "ledger/",
        MyLedgerEntriesView.as_view(),
        name="my_ledger",
    ),
    path(
        "ledger-audit/",
        LedgerAuditView.as_view(),
        name="ledger_audit",
    ),
    path(
        "transactions/<str:reference>/",
        TransactionDetailView.as_view(),
        name="transaction_detail",
    ),
]
