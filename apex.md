# Apex Bank — Banking Simulator

Apex Bank is a mock fintech banking simulator built for learning and testing purposes. It looks and feels like a real modern fintech app (Revolut / Kuda / Stripe style). Built in phases with Django + PostgreSQL.

## Run & Operate

- `Start application` workflow — Django dev server on port 8000 (`cd banking && python manage.py runserver 0.0.0.0:8000`)
- Local Windows: `cd banking && .\run-dev.ps1` (SQLite + http://127.0.0.1:8000)
- `cd banking && python manage.py makemigrations <app>` — create new migrations
- `cd banking && python manage.py migrate` — apply migrations
- `cd banking && python manage.py createsuperuser` — create an admin/staff user
- Required env: `DATABASE_URL` — PostgreSQL connection string (already configured)
- Required env: `SESSION_SECRET` — used as Django's `SECRET_KEY`

## Stack

- Python 3.11, Django 5.2
- Database: PostgreSQL via psycopg2-binary + dj-database-url
- Templates: Django templates (two base layouts: `base.html` for auth, `base_app.html` for app)
- CSS: Custom design system (no framework dependency — all inline/custom CSS in base templates)
- Icons: Bootstrap Icons (CDN)
- Charts: Chart.js (CDN, admin dashboard only)
- Font: Inter (Google Fonts CDN)
- Auth: Django built-in auth system with custom email-based user model

## URL Structure

| Path | View | Notes |
|------|------|-------|
| `/` | → `/dashboard/` redirect | |
| `/accounts/login/` | CustomLoginView | Auth page |
| `/accounts/register/` | RegisterView | Auth page |
| `/accounts/logout/` | CustomLogoutView | POST only |
| `/dashboard/` | DashboardView | Requires login |
| `/transfers/` | TransferView | Send money |
| `/transfers/history/` | TransactionHistoryView | Search, filters, newest first |
| `/transfers/statement/` | AccountStatementView | Account statement |
| `/transfers/transactions/<ref>/` | TransactionDetailView | Ownership-checked detail |
| `/profile/` | ProfileView | User info + password change |
| `/profile/password/` | ChangePasswordView | POST handler |
| `/admin-dashboard/` | AdminDashboardView | Staff only |
| `/admin/` | Django admin | Staff only |

## Where things live

- `banking/banking_project/settings.py` — central config (DB, apps, auth, CSRF, cookie settings)
- `banking/banking_project/urls.py` — root URL router
- `banking/banking_project/middleware.py` — PartitionedCookiesMiddleware (CHIPS for iframe)
- `banking/accounts/models.py` — CustomUser (email-based login)
- `banking/accounts/views.py` — Auth + Dashboard + Profile + AdminDashboard views
- `banking/accounts/urls.py` — /accounts/register|login|logout/
- `banking/accounts/dashboard_urls.py` — /dashboard/
- `banking/accounts/profile_urls.py` — /profile/ and /profile/password/
- `banking/accounts/admin_urls.py` — /admin-dashboard/
- `banking/bank_accounts/models.py` — Account model (OneToOne to user, auto-created via signal)
- `banking/transfers/models.py` — Transaction model (immutable audit record)
- `banking/transfers/forms.py` — TransferForm (to_account_number, amount, note)
- `banking/transfers/selectors.py` — History queries + ownership checks
- `banking/transfers/views.py` — Transfer, history, statement, detail views
- `banking/transfers/urls.py` — /transfers/, /history/, /statement/, /transactions/<ref>/
- `banking/templates/base.html` — Auth layout (split-screen: blue panel + form)
- `banking/templates/base_app.html` — App layout (sidebar desktop, bottom nav mobile)
- `banking/templates/accounts/` — login.html, register.html, dashboard.html, profile.html, admin_dashboard.html
- `banking/templates/transfers/` — transfer.html, history.html, statement.html, transaction_detail.html

## Design System

- **Primary:** Deep Blue (`#1E40AF`)
- **Secondary:** Emerald Green (`#10B981`)
- **Sidebar:** Dark navy (`#0F172A`)
- **Page bg:** `#F1F5F9`
- **Cards:** White, `border-radius: 1rem`, subtle shadow
- **Sidebar:** 260px wide, fixed left, dark — collapsible on mobile
- **Bottom nav:** Fixed bottom on mobile (Home, Send, History, Profile)
- Auth pages use `base.html` (split-screen, no sidebar)
- App pages use `base_app.html` (sidebar + bottom nav)

## Architecture Decisions

- **Custom user model from day one** — email as login credential; `AUTH_USER_MODEL` set before any migrations.
- **App-per-concern** — accounts, bank_accounts, transfers; each phase is its own app.
- **CSRF_USE_SESSIONS = True** — CSRF token stored server-side in session; eliminates the separate `csrftoken` cookie which Django 5.2 can't stamp with `Partitioned` natively.
- **CHIPS cookies** — `PartitionedCookiesMiddleware` monkey-patches `Morsel._reserved` + `Morsel._flags` to stamp `SameSite=None; Secure; Partitioned` on the session cookie, enabling the app to work inside the Replit cross-origin iframe.
- **Middleware order** — `PartitionedCookiesMiddleware` is listed FIRST in MIDDLEWARE so it runs LAST on responses (after `SessionMiddleware` has set the cookie).
- **transaction.atomic + select_for_update** — transfers lock both account rows before touching balances, preventing race conditions and guaranteeing money conservation.
- **Transaction.on_delete=PROTECT** — financial records can never be silently deleted by cascading user/account deletion.
- **dj-database-url** — reads DATABASE_URL env var; no credentials hardcoded.

## Phases

- **Phase 1 ✅** — User registration, login, logout, dashboard
- **Phase 2 ✅** — Bank accounts (auto-created via signal, account numbers, balances)
- **Phase 3 ✅** — Transfers (atomic, race-condition-safe)
- **Phase 4 ✅** — Transaction history, account statement, transaction detail page (ownership-checked)
- **Phase 5 ✅** — Search (reference, amount, account), filters, pagination, statement summaries
- **Phase 6** — Ledger system (future)
- **Design ✅** — Full fintech UI redesign (Revolut/Kuda/Stripe style), all 8 screens

## Gotchas

- Django 5+ requires logout via POST (CSRF) — all logout buttons are `<form method="post">`.
- `CSRF_COOKIE_PARTITIONED` does NOT exist in Django 5.2 — `CSRF_USE_SESSIONS` is the correct fix.
- `Morsel._flags.add("partitioned")` is required alongside `_reserved` — without it Python outputs `Partitioned=True` (invalid) instead of bare `Partitioned`.
- Migrations: `makemigrations <app_name>` then `migrate` after any model change.
- Future ForeignKeys to user: always `ForeignKey(settings.AUTH_USER_MODEL)`, never `ForeignKey(User)`.
- Admin dashboard at `/admin-dashboard/` requires `is_staff=True` on the user.
