"""
transfers/urls.py — URL patterns for the transfers app.
Mounted at /transfers/ in banking_project/urls.py.
"""

from django.urls import path

from .views import TransferView, TransactionHistoryView

urlpatterns = [
    path("",        TransferView.as_view(),            name="transfer"),
    path("history/", TransactionHistoryView.as_view(), name="history"),
]
