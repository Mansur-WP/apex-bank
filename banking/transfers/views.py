"""
transfers/views.py — Transfers, history, statement, and transaction detail views.
"""

from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View

from .forms import TransferForm
from .selectors import (
    TransactionFilters,
    get_recent_transactions,
    get_transaction_for_account,
    get_transaction_page,
    statement_period_label,
    verify_recipient_account,
)
from .services import (
    InsufficientFundsError,
    ReceiverNotFoundError,
    SelfTransferError,
    TransferError,
    execute_transfer,
)


def _get_user_account(user):
    """Return the logged-in user's bank account or None."""
    try:
        return user.account
    except ObjectDoesNotExist:
        return None


def _filters_query_string(filters: TransactionFilters) -> str:
    return urlencode(filters.query_dict())


def _transaction_list_context(account, request, result):
    """Shared template context for history and statement views."""
    return {
        "account": account,
        "rows": result.rows,
        "page_obj": result.page_obj,
        "summary": result.summary,
        "filters": result.filters,
        "filter_query": _filters_query_string(result.filters),
        "period_label": statement_period_label(
            result.filters.date_from,
            result.filters.date_to,
        ),
    }


class VerifyRecipientView(LoginRequiredMixin, View):
    """
    JSON endpoint: verify recipient account number before transfer.

    GET /transfers/verify/?account_number=1234567890
  """

    login_url = "/accounts/login/"

    def get(self, request):
        sender_account = _get_user_account(request.user)
        if sender_account is None:
            return JsonResponse(
                {"status": "error", "message": "No bank account linked to your profile."},
                status=400,
            )

        account_number = request.GET.get("account_number", "")
        result = verify_recipient_account(account_number, sender_account)
        status_code = 200 if result.status == "found" else 200
        return JsonResponse(result.to_dict(), status=status_code)


class TransferView(LoginRequiredMixin, View):
    login_url = "/accounts/login/"
    template_name = "transfers/transfer.html"

    def get(self, request):
        account = _get_user_account(request.user)
        if account is None:
            messages.error(
                request,
                "No bank account is linked to your profile. Please contact support.",
            )
            return redirect("dashboard")

        return render(request, self.template_name, {
            "form": TransferForm(),
            "account": account,
        })

    def post(self, request):
        form = TransferForm(request.POST)
        sender_account = _get_user_account(request.user)

        if sender_account is None:
            messages.error(
                request,
                "No bank account is linked to your profile. Please contact support.",
            )
            return redirect("dashboard")

        if not form.is_valid():
            messages.error(request, "Please correct the errors below and try again.")
            return render(request, self.template_name, {
                "form": form,
                "account": sender_account,
            })

        to_account_number = form.cleaned_data["to_account_number"]
        amount = form.cleaned_data["amount"]
        note = form.cleaned_data.get("note", "")

        try:
            result = execute_transfer(
                sender_account,
                to_account_number,
                amount,
                note=note,
            )
        except ReceiverNotFoundError:
            form.add_error("to_account_number", "No account found with that number.")
            messages.error(request, "Transfer failed: recipient account not found.")
            return render(request, self.template_name, {
                "form": form,
                "account": sender_account,
            })
        except SelfTransferError:
            form.add_error(
                "to_account_number",
                "You cannot transfer money to your own account.",
            )
            messages.error(request, "Transfer failed: you cannot send money to yourself.")
            return render(request, self.template_name, {
                "form": form,
                "account": sender_account,
            })
        except InsufficientFundsError as exc:
            form.add_error(
                "amount",
                f"Insufficient funds. Available balance: ₦{exc.available:,.2f}.",
            )
            messages.error(
                request,
                f"Transfer failed: insufficient funds (available ₦{exc.available:,.2f}).",
            )
            return render(request, self.template_name, {
                "form": form,
                "account": sender_account,
            })
        except TransferError as exc:
            messages.error(request, f"Transfer failed: {exc}")
            return render(request, self.template_name, {
                "form": form,
                "account": sender_account,
            })

        txn = result.transaction
        messages.success(
            request,
            f"Transfer of ₦{amount:,.2f} sent successfully. Reference: {txn.reference}",
        )
        return redirect("dashboard")


class TransactionHistoryView(LoginRequiredMixin, View):
    """Phase 5: searchable, filterable, paginated transaction history."""

    login_url = "/accounts/login/"
    template_name = "transfers/history.html"

    def get(self, request):
        account = _get_user_account(request.user)
        if account is None:
            messages.error(request, "No bank account found for your profile.")
            return redirect("dashboard")

        filters = TransactionFilters.from_request(request)
        page_number = request.GET.get("page", 1)
        result = get_transaction_page(account, filters, page_number=page_number)

        return render(
            request,
            self.template_name,
            _transaction_list_context(account, request, result),
        )


class AccountStatementView(LoginRequiredMixin, View):
    """Phase 5: account statement with summary statistics and paginated table."""

    login_url = "/accounts/login/"
    template_name = "transfers/statement.html"

    def get(self, request):
        account = _get_user_account(request.user)
        if account is None:
            messages.error(request, "No bank account found for your profile.")
            return redirect("dashboard")

        filters = TransactionFilters.from_request(request)
        page_number = request.GET.get("page", 1)
        result = get_transaction_page(account, filters, page_number=page_number)

        return render(
            request,
            self.template_name,
            _transaction_list_context(account, request, result),
        )


class TransactionDetailView(LoginRequiredMixin, View):
    """
    Phase 4: dedicated transaction detail page.

    Ownership is enforced in get_transaction_for_account — other users get 404.
    """

    login_url = "/accounts/login/"
    template_name = "transfers/transaction_detail.html"

    def get(self, request, reference):
        account = _get_user_account(request.user)
        if account is None:
            messages.error(request, "No bank account found for your profile.")
            return redirect("dashboard")

        row = get_transaction_for_account(account, reference)

        return render(request, self.template_name, {
            "row": row,
            "account": account,
        })
