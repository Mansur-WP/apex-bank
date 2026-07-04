# 🧪 Apex Bank — Test Strategy

> **Document Owner:** Staff Fintech Engineer  
> **Last Updated:** July 4, 2026  
> **Status:** Living Document  
> **Framework:** Django `TestCase`

---

## 1. Overview

Because Apex Bank processes financial data, testing is paramount. A single logic error in the transfer engine can lead to money creation, destruction, or unauthorized access.

This document outlines our testing philosophy, current coverage, and standards for writing tests.

---

## 2. Testing Philosophy

1. **Test Business Logic Independently:** The core financial engine (`transfers/services.py`) must be tested directly via unit tests, completely bypassing the HTTP/View layer.
2. **Prove Conservation:** Every test involving money movement must explicitly assert that `Total System Balance Before == Total System Balance After`.
3. **Pessimistic Testing:** We assume the system will fail. We write tests for edge cases (zero amount, negative amount, insufficient funds, frozen accounts, self-transfers).
4. **Integration via Views:** After the service layer is verified, views are tested to ensure form binding, HTTP status codes, and user feedback (messages) work correctly.

---

## 3. Current Test Coverage

### 3.1 Financial Engine (`transfers/tests.py`)

The `execute_transfer()` service is thoroughly tested against the following scenarios:

- **Happy Path:** Successful transfer between two active users.
- **Validation Failures:**
  - Transfer amount `0` (fails).
  - Transfer amount `-500` (fails).
  - Transfer with insufficient funds (fails).
  - Transfer to self (fails).
  - Sender account frozen (fails).
- **Concurrency / Race Conditions:** Currently NOT tested due to SQLite limitations.
- **System Conservation:** `test_money_conservation_across_system` proves that the sum of all balances remains constant after a randomized stress test.

### 3.2 Ledger Integration (`transfers/tests_ledger.py`)

- **Double-Entry Verification:** Ensures that exactly two `LedgerEntry` records (1 DEBIT, 1 CREDIT) are created per successful transaction.
- **Ledger Reversal:** Verifies that a failed transaction produces ZERO ledger entries and leaves balances unchanged.

### 3.3 Authorization & Access Control

- **Transaction Ownership:** Tests verify that User A cannot view User B's transaction details.
- **Admin Access:** Tests verify that non-staff users cannot access admin views.

---

## 4. Known Gaps & Action Items

| Component | Status | Action Required |
|---|---|---|
| `accounts` models | 🟡 Partial | Add tests for `CustomUser` creation, string representation, and `generate_account_number()` collision handling. |
| `accounts` views | 🔴 Missing | Add tests for registration, login, profile updates, and password changes. |
| `bank_accounts` signals | 🔴 Missing | Add explicit tests verifying `Account` auto-creation on user registration. |
| Admin Actions | 🔴 Missing | Add tests for `freeze_account()` and `unfreeze_account()` ensuring dual-state synchronization. |
| Concurrency | 🔴 Missing | Move test database to PostgreSQL to test `select_for_update()` deadlocks and race conditions. |

---

## 5. Writing Tests

### 5.1 Setting Up Data

Use Django's `setUp()` method to create standard test fixtures.

```python
def setUp(self):
    self.alice = CustomUser.objects.create_user(...)
    self.bob = CustomUser.objects.create_user(...)
    # Wait for signals to run, then retrieve auto-created accounts
    self.alice_account = Account.objects.get(user=self.alice)
    self.bob_account = Account.objects.get(user=self.bob)
```

### 5.2 Asserting Balances

Always assert the exact expected balance after an operation, rather than just checking that a transfer didn't crash.

```python
self.alice_account.refresh_from_db()
self.assertEqual(self.alice_account.balance, Decimal("9500.00"))
```

### 5.3 Testing Exceptions

When testing service layer validation failures, use `assertRaisesMessage`:

```python
with self.assertRaisesMessage(TransferError, "Account is frozen"):
    execute_transfer(...)
```

---

## 6. Continuous Integration (Planned)

Once a CI/CD pipeline (e.g., GitHub Actions) is implemented:

1. Tests must run on every Pull Request.
2. The test database MUST be PostgreSQL (to validate row-level locking).
3. Coverage thresholds should be enforced (`coverage run manage.py test`).
4. Minimum coverage target for `transfers/services.py` is **100%**.
