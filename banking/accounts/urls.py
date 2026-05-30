"""
urls.py — URL patterns for the accounts app (auth routes).

Why it exists:
    Keeping auth routes in this file and including them under /accounts/
    in the root urls.py follows Django's app-per-concern convention.
    The accounts app owns everything under /accounts/.

What it does:
    Maps URL paths to the view classes defined in accounts/views.py.

How it connects:
    Included by banking_project/urls.py as:
        path("accounts/", include("accounts.urls"))

    The `name` argument on each path creates a named URL that templates
    and views can reference with {% url 'register' %} and reverse().
"""

from django.urls import path
from .views import RegisterView, CustomLoginView, CustomLogoutView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/",    CustomLoginView.as_view(), name="login"),
    path("logout/",   CustomLogoutView.as_view(), name="logout"),
]
