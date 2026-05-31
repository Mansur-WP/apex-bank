"""
urls.py — Root URL configuration for Apex banking simulator.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),

    # Authentication
    path("accounts/", include("accounts.urls")),

    # Dashboard (top-level so other apps live at their own paths)
    path("dashboard/", include("accounts.dashboard_urls")),

    # Phase 3: transfers and transaction history
    path("transfers/", include("transfers.urls")),

    # Profile
    path("profile/",  include("accounts.profile_urls")),

    # Admin dashboard (staff only)
    path("admin-dashboard/", include("accounts.admin_urls")),

    # Root → dashboard
    path("", RedirectView.as_view(url="/dashboard/", permanent=False)),
]
