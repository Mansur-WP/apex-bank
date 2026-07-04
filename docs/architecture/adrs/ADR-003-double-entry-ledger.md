# ADR-003: Double-Entry Ledger System

> **Status:** Accepted  
> **Date:** July 4, 2026  
> **Decision Makers:** Engineering Team  
> **Applies To:** `transfers/models.py`, `transfers/services.py`

---

## Context

To transfer money between User A and User B, the simplest approach is "Single-Entry":
```python
sender.balance -= amount
receiver.balance += amount
```

While simple, this is highly dangerous for financial systems. If the server crashes between the two updates, money is destroyed. If a bug causes only one side to execute, money is created out of thin air. Furthermore, single-entry provides no immutable audit trail of *why* a balance changed.

---

## Decision

Apex Bank implements a **Double-Entry Bookkeeping** system.

Every transfer MUST generate:
1. One `Transaction` record (the header).
2. Exactly two `LedgerEntry` records (the lines):
   - A `DEBIT` entry for the sender.
   - A `CREDIT` entry for the receiver.

### Enforcement

The `execute_transfer()` service enforces a **Conservation Check** before committing the database transaction:
```python
if debit_total != credit_total:
    raise ValueError("Ledger imbalance detected")
```

If this check fails, the entire database transaction is rolled back.

---

## Consequences

### Positive
- **Immutability:** Every financial movement leaves a permanent audit trail.
- **Verification:** Balances can be mathematically proven by summing ledger entries from the beginning of time.
- **Extensibility:** Prepares the system for future account types (Fee Revenue accounts, System Reserve accounts) without altering the core transfer logic.

### Negative
- **Database Size:** Storing 3 rows (1 Transaction, 2 LedgerEntries) instead of 1 row per transfer triples the storage requirements for history.
- **Performance:** Inserts are heavier, requiring more time inside the atomic lock window.

---

## Alternatives Considered

### Alternative 1: Event Sourcing (CQRS)
- **Pro:** Infinite undo, complete history replay.
- **Con:** Immense complexity overhead; requires message brokers and eventual consistency patterns.
- **Verdict:** Overkill for this simulator. Double-entry on relational tables provides 90% of the benefit with 10% of the complexity.
