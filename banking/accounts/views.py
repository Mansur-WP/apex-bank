"""
views.py — View logic for user registration, login, logout, and dashboard.

Why it exists:
    Views are the "controller" layer in Django's MVT pattern. They receive
    HTTP requests, interact with models/forms, and return rendered responses.

What it does:
    RegisterView    — handles GET (show form) and POST (validate + create user)
    CustomLoginView — wraps Django's LoginView to use our LoginForm
    CustomLogoutView — wraps Django's LogoutView (POST-only for CSRF safety)
    DashboardView   — login-required page; passes user + bank account to template

How it connects:
    - URLs in accounts/urls.py and accounts/dashboard_urls.py map paths to
      these view classes.
    - Forms from accounts/forms.py handle validation logic.
    - Templates in templates/accounts/ handle rendering.
    - settings.LOGIN_URL, LOGIN_REDIRECT_URL, LOGOUT_REDIRECT_URL control
      where redirects land.

Phase 2 changes:
    DashboardView.get_context_data() now fetches the user's Account via the
    reverse OneToOne accessor (request.user.account) and passes it to the
    template. A try/except guards against the rare case where the account
    does not exist yet (e.g. a user created before Phase 2 was deployed).

Scalability note:
    Phase 3 (transfers) will extend get_context_data() to also inject recent
    transactions. The view's structure stays the same — only the context grows.
"""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .forms import LoginForm, RegistrationForm


class RegisterView(CreateView):
    """
    User registration view.

    GET  — renders the blank registration form.
    POST — validates input, creates the user, logs them in automatically,
           and redirects to the dashboard.

    The post_save signal on CustomUser (bank_accounts/signals.py) fires
    immediately after super().form_valid() saves the user, so by the time
    the user reaches the dashboard the bank account already exists.
    """

    form_class = RegistrationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(
            self.request,
            f"Welcome, {self.object.get_short_name()}! Your account has been created.",
        )
        return response

    def dispatch(self, request, *args, **kwargs):
        """Redirect already-authenticated users away from the register page."""
        if request.user.is_authenticated:
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)


class CustomLoginView(LoginView):
    """
    Login view — wraps Django's built-in LoginView with our email-based form.
    All brute-force protection and session management is inherited.
    """
    form_class = LoginForm
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    """
    Logout view — POST-only (Django 5 CSRF requirement).
    LOGOUT_REDIRECT_URL in settings controls where users land afterward.
    """
    pass


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Main dashboard — the landing page after login.

    LoginRequiredMixin redirects unauthenticated users to LOGIN_URL
    automatically. No manual auth check needed.

    Context injected into the template:
        user    — the logged-in CustomUser instance
        account — the user's Account instance (Phase 2), or None if missing

    Phase 2: account is fetched via the reverse OneToOne accessor
    `request.user.account`. The RelatedObjectDoesNotExist exception is caught
    so the dashboard degrades gracefully for any user who somehow lacks an
    account (e.g. data created before the signal was in place).
    """

    template_name = "accounts/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user

        # Fetch the linked bank account via the reverse OneToOne accessor.
        # If no account exists (edge case), pass None so the template can
        # show a graceful fallback instead of raising an unhandled exception.
        try:
            context["account"] = self.request.user.account
        except self.request.user.__class__.account.RelatedObjectDoesNotExist:
            context["account"] = None

        return context
