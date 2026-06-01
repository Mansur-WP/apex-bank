from django.urls import path, include

from .views import AdminDashboardView

urlpatterns = [
    path("", AdminDashboardView.as_view(), name="admin_dashboard"),
    path("", include("accounts.urls_freeze")),
]

