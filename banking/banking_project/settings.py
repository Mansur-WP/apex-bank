"""
settings.py — Central configuration for the banking simulator.

Why it exists:
    Django requires a settings module to configure every aspect of the
    project: database, installed apps, middleware, templates, auth, etc.

What it does:
    - Reads secrets from environment variables (never hardcoded).
    - Configures PostgreSQL via the DATABASE_URL env var.
    - Registers all installed apps including the custom `accounts` app.
    - Points Django at the project-level templates directory.
    - Declares AUTH_USER_MODEL so Django uses our custom user everywhere.

How it connects:
    Every other Django module (models, views, URLs) implicitly depends on
    this file. manage.py and wsgi.py both reference it by name.

Scalability note:
    Future phases (bank accounts, transfers, ledger) only need to add their
    app to INSTALLED_APPS — no other change to this file is required.
"""

import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------
SECRET_KEY = os.environ.get("SESSION_SECRET", "dev-fallback-key-change-in-prod")

DEBUG = os.environ.get("DEBUG", "True") == "True"

ALLOWED_HOSTS = ["*"]

# Trust the X-Forwarded-Proto header set by Replit's HTTPS proxy so Django
# knows the connection is HTTPS (required for correct CSRF origin checking).
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# Build trusted origins from wildcard patterns plus any explicit domains
# injected by the Replit environment (REPLIT_DOMAINS is comma-separated).
_replit_domains = os.environ.get("REPLIT_DOMAINS", "")
_extra_origins = [
    f"https://{d.strip()}"
    for d in _replit_domains.split(",")
    if d.strip()
]

CSRF_TRUSTED_ORIGINS = [
    "https://*.replit.dev",
    "https://*.repl.co",
    "https://*.replit.app",
] + _extra_origins

# ── Cookie / CSRF policy for cross-origin iframe (Replit preview pane) ───────
#
# Chrome 2024+ blocks ALL third-party cookies in cross-origin iframes —
# including SameSite=None; Secure. Two fixes applied together:
#
#  1. CSRF_USE_SESSIONS — stores the CSRF token inside the server-side
#     session instead of a dedicated csrftoken cookie. Eliminates the CSRF
#     cookie entirely; only the session cookie needs to survive.
#
#  2. Session cookie with Partitioned (CHIPS) — the session cookie is stamped
#     with SameSite=None; Secure; Partitioned by PartitionedCookiesMiddleware
#     in banking_project/middleware.py. Partitioned cookies are stored per
#     top-level site, which exempts them from third-party cookie blocking.
#
# Django 5.2's CSRF middleware source does NOT contain native Partitioned
# support for the CSRF cookie; CSRF_USE_SESSIONS sidesteps that entirely.

CSRF_USE_SESSIONS = True          # CSRF token lives in the session, not a cookie

SESSION_COOKIE_SAMESITE = "None"  # Required for cross-origin iframe access
SESSION_COOKIE_SECURE = True      # Required when SameSite=None
SESSION_COOKIE_PARTITIONED = True # Django 5.1+ — CHIPS; middleware also enforces

# ---------------------------------------------------------------------------
# Application definition
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Phase 1: authentication and user management
    "accounts",
    # Phase 2: bank account layer
    "bank_accounts",
    # Phase 3: money transfers
    "transfers",
]

MIDDLEWARE = [
    # PartitionedCookiesMiddleware MUST come before SessionMiddleware.
    # Django processes responses in reverse-list order, so listing it first
    # ensures it runs last on responses — after Session has set its cookie.
    "banking_project.middleware.PartitionedCookiesMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "banking_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Project-level templates directory — shared across all apps.
        # Each app can also have its own templates/ subdirectory.
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "banking_project.wsgi.application"

# ---------------------------------------------------------------------------
# Database — PostgreSQL via DATABASE_URL environment variable
# ---------------------------------------------------------------------------
DATABASES = {
    "default": dj_database_url.config(
        env="DATABASE_URL",
        conn_max_age=600,
    )
}

# ---------------------------------------------------------------------------
# Custom user model
# Declaring this early means Django and every third-party package will
# use CustomUser instead of the built-in User everywhere — including
# ForeignKey references in future bank account and transaction models.
# ---------------------------------------------------------------------------
AUTH_USER_MODEL = "accounts.CustomUser"

# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------------
# Auth redirect URLs
# ---------------------------------------------------------------------------
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
