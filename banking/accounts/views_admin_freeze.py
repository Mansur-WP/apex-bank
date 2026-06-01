from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.views import View

from .admin_actions import freeze_account, unfreeze_account

from bank_accounts.models import Account


class FreezeAccountView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = "/accounts/login/"

    def test_func(self):
        return self.request.user.is_staff

    def post(self, request):
        account_number = request.POST.get("account_number", "").strip()
        if not account_number:
            messages.error(request, "Account number is required.")
            return redirect("admin_dashboard")

        try:
            freeze_account(acting_user=request.user, account_number=account_number)
            messages.success(request, f"Account {account_number} frozen.")
        except Account.DoesNotExist:
            messages.error(request, "Account not found.")
        except Exception as exc:
            messages.error(request, str(exc))

        return redirect("admin_dashboard")


class UnfreezeAccountView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = "/accounts/login/"

    def test_func(self):
        return self.request.user.is_staff

    def post(self, request):
        account_number = request.POST.get("account_number", "").strip()
        if not account_number:
            messages.error(request, "Account number is required.")
            return redirect("admin_dashboard")

        try:
            unfreeze_account(acting_user=request.user, account_number=account_number)
            messages.success(request, f"Account {account_number} unfrozen.")
        except Account.DoesNotExist:
            messages.error(request, "Account not found.")
        except Exception as exc:
            messages.error(request, str(exc))

        return redirect("admin_dashboard")

