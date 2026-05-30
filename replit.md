# Apex — Banking Simulator

Apex is a mock banking simulator built for learning and testing purposes. It is not a real bank but looks and feels like one. Built in phases with Django + PostgreSQL.

## Run & Operate

- `Start application` workflow — runs the Django dev server on port 8000
- `cd banking && python manage.py runserver 0.0.0.0:8000` — manual start
- `cd banking && python manage.py makemigrations` — create new migrations
- `cd banking && python manage.py migrate` — apply migrations
- `cd banking && python manage.py createsuperuser` — create an admin user
- Required env: `DATABASE_URL` — PostgreSQL connection string (already configured)

## Stack

- Python 3.11, Django 5.2
- Database: PostgreSQL via psycopg2-binary + dj-database-url
- Templates: Django templates + Bootstrap 5 (CDN)
- Auth: Django's built-in auth system with a custom user model (email-based)

## Where things live

- `banking/` — Django project root
- `banking/banking_project/settings.py` — central configuration (DB, apps, auth)
- `banking/banking_project/urls.py` — root URL router
- `banking/accounts/models.py` — CustomUser model (source of truth for users)
- `banking/accounts/views.py` — RegisterView, LoginView, LogoutView, DashboardView
- `banking/accounts/forms.py` — RegistrationForm, LoginForm
- `banking/accounts/urls.py` — /accounts/register|login|logout/
- `banking/accounts/dashboard_urls.py` — /dashboard/
- `banking/templates/base.html` — master layout (nav, Bootstrap, messages)
- `banking/templates/accounts/` — register.html, login.html, dashboard.html
- `banking/requirements.txt` — Python dependencies

## Architecture decisions

- **Custom user model from day one** — uses email (not username) as login credential; declared as `AUTH_USER_MODEL` before any migrations so future ForeignKeys use `settings.AUTH_USER_MODEL` without painful retrofitting.
- **App-per-concern structure** — each phase gets its own Django app (accounts, bank_accounts, transfers, ledger); root `urls.py` stays clean with one `include()` per app.
- **Dashboard URL at top level** — `/dashboard/` lives outside `/accounts/` so Phase 2+ apps can live at `/bank/`, `/transfers/`, `/ledger/` without URL nesting.
- **dj-database-url** — reads DATABASE_URL env var; no credentials hardcoded anywhere.
- **Class-based views** — RegisterView, LoginView, LogoutView, DashboardView all use CBVs for clean extension in future phases.

## Product

Phase 1: User registration, login, logout, and a dashboard showing full name and email.

Future phases:
- Phase 2: Bank accounts (checking/savings)
- Phase 3: Transfers and transaction history
- Phase 4: Ledger system

## User preferences

_Populate as you build._

## Gotchas

- Django 5+ requires logout via POST (CSRF protection) — the base template includes a form for this.
- Always run `makemigrations accounts` then `migrate` after changing `accounts/models.py`.
- Future model ForeignKeys to the user must use `ForeignKey(settings.AUTH_USER_MODEL)`, never `ForeignKey(User)`.
- `SESSION_SECRET` env var is used as Django's `SECRET_KEY`.

## Pointers

- See the `pnpm-workspace` skill for the existing Node.js monorepo context
