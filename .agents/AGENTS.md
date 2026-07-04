# Apex Bank AI Agent Context Rules

This file provides system context, architectural guidelines, and strict rules for any AI agent interacting with the Apex Bank codebase.

## 1. Project Context
- **Name:** Apex Bank
- **Type:** Digital Banking Simulator (Portfolio Project)
- **Framework:** Django 5.2 / Python 3.11
- **Key Feature:** Double-entry ledger with atomic transfers
- **Rule:** Never treat this as a simple CRUD app. Financial integrity is the absolute highest priority.

## 2. Architectural Boundaries
We strictly follow the **Service/Selector pattern**:
- **Views (`views.py`):** ONLY handle HTTP. Extract data, call services/selectors, return response.
- **Services (`services.py`):** ONLY handle writes. Never access `request`. Must use `transaction.atomic()`.
- **Selectors (`selectors.py`):** ONLY handle reads. Must not change any state.

## 3. Financial Integrity Rules (Non-Negotiable)
When modifying `transfers/services.py` or related logic:
1. **Double-Entry:** Every transaction MUST create exactly two `LedgerEntry` records (1 DEBIT, 1 CREDIT).
2. **Conservation Check:** You MUST verify `debit_total == credit_total` before committing.
3. **Row Locking:** You MUST use `select_for_update()` on `Account` rows when modifying balances.
4. **Lock Ordering:** You MUST order locked rows by Primary Key (`order_by("pk")`) to prevent deadlocks.
5. **No Overdrafts:** Sender balance must be checked *after* acquiring the row lock.

## 4. Frozen State Syncing
- **Canonical Source:** `bank_accounts.Account.status` is the source of truth for frozen accounts.
- **Mirror:** `accounts.CustomUser.is_frozen` is a mirror for fast querying.
- **Rule:** If you freeze or unfreeze an account, you MUST update BOTH fields. Use `accounts.admin_actions.freeze_account()` rather than updating the ORM directly.

## 5. Coding Standards
- **Docstrings:** Use the "Why / What / How" format for all new modules, models, and services.
- **Models:** Never delete financial records. Use `PROTECT` on foreign keys for `Transaction` and `LedgerEntry`.

## 6. Testing
- If you modify the transfer engine, you must run `python manage.py test banking.transfers`.
- Test balance conservation explicitly in your unit tests.
