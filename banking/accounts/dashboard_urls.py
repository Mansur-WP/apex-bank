"""
dashboard_urls.py — URL pattern for the dashboard.

Why it exists:
    The dashboard lives at /dashboard/ (top-level path) rather than
    /accounts/dashboard/ so future phases can co-exist cleanly:
        /bank/      — bank accounts (Phase 2)
        /transfers/ — transfers (Phase 3)
        /ledger/    — ledger (Phase 4)
    Keeping the dashboard URL separate from accounts/ makes this layout
    natural and avoids a deeply nested URL scheme.

What it does:
    Registers a single URL pattern for the DashboardView.

How it connects:
    Included by banking_project/urls.py as:
        path("dashboard/", include("accounts.dashboard_urls"))
"""

from django.urls import path
from .views import DashboardView

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
]
