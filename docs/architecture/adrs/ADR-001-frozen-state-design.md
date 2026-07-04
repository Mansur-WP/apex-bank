# ADR-001: Frozen Account State — Dual-Source Design

> **Status:** Accepted  
> **Date:** July 4, 2026  
> **Decision Makers:** Engineering Team  
> **Applies To:** `accounts.CustomUser.is_frozen` and `bank_accounts.Account.status`

---

## Context

Apex Bank needs the ability for staff/admin users to freeze a bank account, preventing the account holder from sending money. The question is: where should the "frozen" state live?

Two candidates exist:

1. **`accounts.CustomUser.is_frozen`** — A boolean flag on the user model
2. **`bank_accounts.Account.status`** — A `TextChoices` field on the account model (`active` / `frozen`)

These represent different domain concepts:
- **User-level freeze:** The person is frozen (all accounts, if multi-account were supported)
- **Account-level freeze:** A specific bank account is frozen (the user can still log in)

---

## Decision

**`bank_accounts.Account.status` is the canonical source of truth for frozen state.**

The `accounts.CustomUser.is_frozen` field exists as a **backward-compatibility mirror** and MUST always be kept in sync by the `freeze_account()` and `unfreeze_account()` functions in `accounts/admin_actions.py`.

### Enforcement Rules

| Operation | Check Point | Field Checked |
|---|---|---|
| Transfer execution | `transfers/services.py` → `execute_transfer()` | `Account.status == AccountStatus.FROZEN` |
| Admin freeze action | `accounts/admin_actions.py` → `freeze_account()` | Sets `Account.status` AND mirrors to `CustomUser.is_frozen` |
| Admin unfreeze action | `accounts/admin_actions.py` → `unfreeze_account()` | Sets `Account.status` AND mirrors to `CustomUser.is_frozen` |

### Why Not Remove `CustomUser.is_frozen`?

1. It was added early in development before `Account.status` existed
2. Existing code or templates may reference `user.is_frozen`
3. It provides a quick user-level query without JOINing to the accounts table
4. It is indexed (`db_index=True`) for efficient filtering

---

## Consequences

### Positive
- Single source of truth (`Account.status`) is clear
- Mirroring keeps user-level queries fast
- Both freeze and unfreeze are centralized in `admin_actions.py`

### Negative
- **Two fields must stay in sync** — if one is updated without the other, the system is inconsistent
- **All freeze/unfreeze operations MUST go through `admin_actions.py`** — direct ORM updates to either field will break consistency
- Tests that set `CustomUser.is_frozen = True` without also setting `Account.status = FROZEN` will produce incorrect behavior

### Risks

> [!WARNING]
> **Known Test Issue:** `transfers/tests.py` line 99–109 sets `self.alice.is_frozen = True` on the user model but does NOT update `Account.status`. Since `execute_transfer()` checks `Account.status` (the canonical source), this test likely does not behave as intended. The test should use `freeze_account()` from `admin_actions.py` instead of directly setting the field.

---

## Alternatives Considered

### Alternative 1: Remove `CustomUser.is_frozen`, use only `Account.status`
- **Pro:** Single source of truth, no sync risk
- **Con:** Requires migration, template changes, and loss of user-level indexed query
- **Verdict:** Recommended for a future refactoring phase

### Alternative 2: Remove `Account.status`, use only `CustomUser.is_frozen`
- **Pro:** Simpler model
- **Con:** Freezing is a financial operation — it belongs on the financial model, not the identity model
- **Verdict:** Rejected — violates domain separation

### Alternative 3: Derive `is_frozen` via a property (no stored field)
```python
class CustomUser(AbstractBaseUser):
    @property
    def is_frozen(self):
        return hasattr(self, 'account') and self.account.status == AccountStatus.FROZEN
```
- **Pro:** No sync needed
- **Con:** Requires a JOIN for every check, not indexable
- **Verdict:** Viable for future consideration

---

## Action Items

- [ ] Fix `transfers/tests.py` to use `freeze_account()` instead of direct field assignment
- [ ] Add database-level trigger or application-level validation to prevent direct updates to either frozen field outside of `admin_actions.py`
- [ ] Consider migration to Alternative 1 (remove `CustomUser.is_frozen`) in a future phase
