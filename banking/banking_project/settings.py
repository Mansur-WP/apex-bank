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

CSRF_TRUSTED_ORIGINS = [
    "https://*.replit.dev",
    "https://*.repl.co",
    "https://*.replit.app",
]

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
]

MIDDLEWARE = [
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
