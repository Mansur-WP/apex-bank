"""
urls.py — Root URL configuration for the banking simulator.

Why it exists:
    Django uses this file as the top-level URL router. Every incoming HTTP
    request is matched against the patterns defined here.

What it does:
    - Routes /admin/ to Django's built-in admin site.
    - Routes /accounts/ to the accounts app's URL patterns.
    - Routes /dashboard/ to the accounts dashboard view.
    - Redirects the root path (/) to the dashboard.

How it connects:
    Imports accounts.urls and delegates account-specific routing there.
    Future apps (bank accounts, transfers, ledger) will each add an
    include() entry here — this file stays clean.

Scalability note:
    Add future phases as new include() blocks:
        path("bank/", include("bank_accounts.urls")),
        path("transfers/", include("transfers.urls")),
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),

    # All authentication routes live in the accounts app
    path("accounts/", include("accounts.urls")),

    # Dashboard — defined in accounts but lives at the top level
    # so future apps can co-exist at their own paths cleanly
    path("dashboard/", include("accounts.dashboard_urls")),

    # Root redirect: visiting / sends the user to the dashboard
    # (which itself redirects to login if not authenticated)
    path("", RedirectView.as_view(url="/dashboard/", permanent=False)),
]
