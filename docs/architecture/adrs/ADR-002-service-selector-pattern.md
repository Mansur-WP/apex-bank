# ADR-002: Service/Selector Architecture Pattern

> **Status:** Accepted  
> **Date:** July 4, 2026  
> **Decision Makers:** Engineering Team  
> **Applies To:** Entire codebase, specifically `transfers/` and `accounts/`

---

## Context

Django's default architecture is "Model-View-Template" (MVT). A common anti-pattern in Django applications is placing complex business logic directly into Views (fat views) or Models (fat models). 

For a banking application, the transfer execution process involves multiple steps:
1. Validating business rules (sufficient funds, not frozen, etc.)
2. Locking database rows to prevent race conditions
3. Updating multiple tables (Transactions, LedgerEntries, Accounts)
4. Enforcing money conservation checks

Placing this inside `TransferView.post()` makes the logic impossible to test without an HTTP request and difficult to reuse (e.g., if we later add an API or CLI command to execute transfers).

---

## Decision

We adopt the **Service/Selector pattern** (often associated with the Django Styleguide by HackSoft) to decouple business logic from the HTTP layer.

### 1. Services (Write Operations)
- Placed in `services.py`.
- Handle operations that change database state (INSERT, UPDATE, DELETE).
- E.g., `execute_transfer()`, `freeze_account()`.
- **Rules:**
  - Cannot access the `request` object.
  - Return plain Python objects, DataClasses, or Model instances.
  - Handle their own database transactions (`transaction.atomic()`).

### 2. Selectors (Read Operations)
- Placed in `selectors.py`.
- Handle complex queries (SELECT).
- E.g., `get_transaction_history()`, `compute_statement_summary()`.
- **Rules:**
  - Cannot access the `request` object.
  - Perform NO state changes (read-only).
  - Encapsulate complex ORM queries, annotations, and aggregations.

### 3. Views (HTTP Interface)
- Remain "thin".
- Responsible ONLY for:
  - Extracting data from `request` (POST data, GET params, user).
  - Calling Services or Selectors.
  - Handling exceptions raised by Services.
  - Returning HTTP responses (templates, redirects, JSON).

---

## Consequences

### Positive
- **High Testability:** `execute_transfer()` is tested via unit tests without mocking requests or routing.
- **Reusability:** The same service can be called by the Web View, the upcoming REST API (Phase 10), and management commands.
- **Readability:** Views are very short, focusing only on HTTP concerns.

### Negative
- **More files:** Adds `services.py` and `selectors.py` to each app.
- **Learning curve:** New Django developers may be accustomed to fat models or fat views and need to learn this boundary.

---

## Alternatives Considered

### Alternative 1: Fat Models (Business logic in `Account.transfer_to()`)
- **Pro:** Object-oriented approach, easy to find.
- **Con:** A transfer involves two accounts. Which account owns the method? It blurs responsibilities.
- **Verdict:** Rejected.

### Alternative 2: Fat Views
- **Pro:** Less file jumping.
- **Con:** Untestable outside HTTP, zero reusability.
- **Verdict:** Rejected (Dangerous for financial logic).
