"""
views.py — View logic for user registration, login, logout, and dashboard.

Why it exists:
    Views are the "controller" layer in Django's MVT pattern. They receive
    HTTP requests, interact with models/forms, and return rendered responses.

What it does:
    RegisterView   — handles GET (show form) and POST (validate + create user)
    CustomLoginView — wraps Django's LoginView to use our LoginForm
    CustomLogoutView — wraps Django's LogoutView (POST-only for CSRF safety)
    DashboardView  — login-required page showing user profile info

How it connects:
    - URLs in accounts/urls.py and accounts/dashboard_urls.py map paths to
      these view classes.
    - Forms from accounts/forms.py handle validation logic.
    - Templates in templates/accounts/ handle rendering.
    - settings.LOGIN_URL, LOGIN_REDIRECT_URL, LOGOUT_REDIRECT_URL control
      where redirects land.

Scalability note:
    DashboardView will be extended in future phases to show account balances,
    recent transactions, and quick-transfer actions. Only this view and its
    template need to change — the auth flow stays the same.
"""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .forms import LoginForm, RegistrationForm


class RegisterView(CreateView):
    """
    User registration view.

    GET  — renders the blank registration form.
    POST — validates input, creates the user, logs them in automatically,
           and redirects to the dashboard.

    Using CreateView keeps the boilerplate minimal while giving us a clean
    hook (form_valid) to log the user in right after account creation.
    """

    form_class = RegistrationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        """
        Called after successful validation.
        Saves the user, logs them in (so they don't have to log in again
        after registering), then lets the parent redirect to success_url.
        """
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, f"Welcome, {self.object.get_short_name()}! Your account has been created.")
        return response

    def dispatch(self, request, *args, **kwargs):
        """Redirect already-authenticated users away from the register page."""
        if request.user.is_authenticated:
            return self.handle_no_permission() if False else __import__("django.shortcuts", fromlist=["redirect"]).redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)


class CustomLoginView(LoginView):
    """
    Login view.

    Wraps Django's built-in LoginView to:
    - Use our email-based LoginForm.
    - Redirect authenticated users away from the login page.

    All brute-force protection and session management is handled by
    Django's LoginView — we only customise the form and template.
    """

    form_class = LoginForm
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    """
    Logout view.

    Django 5.x requires logout via POST for CSRF safety. The base template
    includes a small form that submits via POST to this view.
    LOGOUT_REDIRECT_URL in settings controls where users land afterward.
    """
    pass


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Main dashboard — the landing page after login.

    LoginRequiredMixin redirects unauthenticated requests to LOGIN_URL
    (configured in settings.py) automatically — no manual check needed.

    Context provided to the template:
        user  — the logged-in CustomUser instance (available automatically
                via Django's auth context processor; listed here for clarity)

    Scalability note:
        In future phases, override get_context_data() to inject account
        balances, recent transactions, and notifications into this view
        without changing the URL config or the login guard.
    """

    template_name = "accounts/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # request.user is the logged-in CustomUser instance.
        # Explicitly passing it here documents the contract for the template.
        context["user"] = self.request.user
        return context
