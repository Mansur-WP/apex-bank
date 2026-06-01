"""transfers/views_ledger.py — Ledger audit and user ledger views."""

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator

from django.shortcuts import redirect, render
from django.views import View

from .models import LedgerEntry


def _get_logged_in_account(request):
    """Return the bank account tied to the current user, or None."""
    try:
        return request.user.account
    except Exception:
        return None


class LedgerAuditView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Staff-only: show all ledger entries across the platform."""

    login_url = "/accounts/login/"
    template_name = "transfers/ledger_entries.html"

    def test_func(self):
        return bool(self.request.user.is_staff)

    def get(self, request):
        page_number = request.GET.get("page", 1)
        qs = (
            LedgerEntry.objects.select_related("transaction", "account")
            .all()
            .order_by("-created_at")
        )
        paginator = Paginator(qs, 15)
        page_obj = paginator.get_page(page_number)

        return render(
            request,
            self.template_name,
            {
                "scope": "admin",
                "rows": page_obj.object_list,
                "page_obj": page_obj,
                "total_count": qs.count(),
                "account": None,
                "filter_query": "",
            },
        )


class MyLedgerEntriesView(LoginRequiredMixin, View):
    """User: show only ledger entries affecting the user's account."""

    login_url = "/accounts/login/"
    template_name = "transfers/ledger_entries.html"

    def get(self, request):
        account = _get_logged_in_account(request)
        if account is None:
            return redirect("dashboard")

        page_number = request.GET.get("page", 1)
        qs = (
            LedgerEntry.objects.select_related("transaction", "account")
            .filter(account=account)
            .order_by("-created_at")
        )
        paginator = Paginator(qs, 15)
        page_obj = paginator.get_page(page_number)

        return render(
            request,
            self.template_name,
            {
                "scope": "user",
                "rows": page_obj.object_list,
                "page_obj": page_obj,
                "total_count": qs.count(),
                "account": account,
                "filter_query": "",
            },
        )

