"""
accounts/views.py — Auth, dashboard, profile, and admin views.
"""

import json
from datetime import timedelta

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Sum
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, TemplateView

from transfers.selectors import get_recent_transactions

from .forms import LoginForm, RegistrationForm


class RegisterView(CreateView):
    form_class = RegistrationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(
            self.request,
            f"Welcome to Apex, {self.object.get_short_name()}! Your account is ready.",
        )
        return response

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    pass


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/dashboard.html"
    login_url = "/accounts/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        try:
            account = self.request.user.account
            context["account"] = account

            context["recent_transactions"] = get_recent_transactions(account, limit=5)
        except ObjectDoesNotExist:
            context["account"] = None
            context["recent_transactions"] = []

        return context


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"
    login_url = "/accounts/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pw_form"] = PasswordChangeForm(self.request.user)
        try:
            context["account"] = self.request.user.account
        except ObjectDoesNotExist:
            context["account"] = None
        return context


class ChangePasswordView(LoginRequiredMixin, View):
    login_url = "/accounts/login/"

    def post(self, request):
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Password changed successfully.")
        else:
            for field_errors in form.errors.values():
                for error in field_errors:
                    messages.error(request, error)
        return redirect("profile")


class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "accounts/admin_dashboard.html"
    login_url = "/accounts/login/"

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        from bank_accounts.models import Account
        from transfers.models import Transaction
        from django.contrib.auth import get_user_model

        User = get_user_model()
        context = super().get_context_data(**kwargs)
        context["total_users"]        = User.objects.count()
        context["total_accounts"]     = Account.objects.count()
        context["total_transactions"] = Transaction.objects.count()
        total_circ = Account.objects.aggregate(total=Sum("balance"))["total"]
        context["total_circulation"]  = total_circ or 0
        context["recent_transactions"] = (
            Transaction.objects
            .select_related("sender_account__user", "receiver_account__user")
            .order_by("-created_at")[:15]
        )

        # Chart data: transactions per day over last 7 days
        now = timezone.now()
        labels, counts = [], []
        for i in range(6, -1, -1):
            day = now - timedelta(days=i)
            labels.append(day.strftime("%b %d"))
            counts.append(Transaction.objects.filter(created_at__date=day.date()).count())
        context["chart_labels"] = json.dumps(labels)
        context["chart_data"]   = json.dumps(counts)

        return context
