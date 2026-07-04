# 📝 Apex Bank — Coding Standards

> **Applies To:** All Apex Bank Python Code

---

## 1. The "Why / What / How" Docstring Standard

All modules, models, services, forms, and significant classes must include a module-level docstring following this exact format:

```python
"""
{module_name.py} — {Brief one-line summary}

Why it exists:
    {Explain the problem this code solves and why it is needed. 
     What would break if this file didn't exist?}

What it does:
    {High-level explanation of the logic, rules, and outputs.}

How it connects:
    {List imports, dependencies, signals triggered, and downstream consumers.}
"""
```

*See `banking/accounts/models.py` or `banking/banking_project/settings.py` for exemplary implementations.*

## 2. Django Model Guidelines

1. **Explicit `__str__` methods:** Every model must define a `__str__` method.
2. **Meta Ordering:** Always specify `class Meta: ordering = [...]` to guarantee predictable querysets.
3. **Foreign Key Protection:** Use `on_delete=models.PROTECT` for all models handling financial data (`Transaction`, `LedgerEntry`). Never use `CASCADE` on a ledger.
4. **Immutability:** Use `editable=False` on fields that should never change after creation (e.g., `account_number`, `transaction_reference`).

## 3. Architecture Boundaries

- **No Fat Views:** Do not place database writes or complex queries inside `views.py`.
- **Service Layer (`services.py`):** Use for all state-changing operations. Must use `transaction.atomic()`. Cannot access `request`.
- **Selector Layer (`selectors.py`):** Use for all read-only complex queries. Cannot access `request`.

## 4. Exceptions

Do not use generic `Exception` for business logic failures. Use the custom exceptions defined in the relevant module (e.g., `TransferError`, `InsufficientFundsError`).
