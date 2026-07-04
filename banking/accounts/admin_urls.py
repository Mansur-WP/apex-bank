from django.urls import path, include

from .views import AdminDashboardView, AdminUsersView, AdminTransactionsView, AdminAccountsView

urlpatterns = [

    path(
        "",
        AdminDashboardView.as_view(),
        name="admin_dashboard"
    ),

    path(
        "users/",
        AdminUsersView.as_view(),
        name="admin_users"
    ),

    path(
        "transactions/",
        AdminTransactionsView.as_view(),
        name="admin_transactions"
    ),

    path(
        "accounts/",
        AdminAccountsView.as_view(),
        name="admin_accounts"
    ),
]