# 📖 Apex Bank — Glossary of Terms

> **Document Owner:** Product Manager  
> **Last Updated:** July 4, 2026

To avoid confusion in code, documentation, and user interfaces, Apex Bank strictly defines the following terminology.

## A
- **Account:** A financial wallet linked to a specific user. It holds a single materialized `balance` and a unique 10-digit `account_number`.
- **Atomic Transaction:** A database operation where either all steps complete successfully, or no steps complete at all. Used in transfers to prevent partial updates.

## B
- **Balance (Materialized):** The cached sum of money in an account, stored directly on the `Account.balance` field for fast read access.
- **Balance (Derived):** The mathematically correct balance calculated by summing all `LedgerEntries` from the beginning of time. Must equal the materialized balance.

## C
- **Conservation Check:** The final validation in `execute_transfer` ensuring that `debit_total == credit_total`.
- **CREDIT:** A ledger entry representing money entering an account (Balance increases).

## D
- **DEBIT:** A ledger entry representing money leaving an account (Balance decreases).
- **Double-Entry Bookkeeping:** The accounting method where every transaction produces at least two equal and opposite ledger entries (debit and credit).

## F
- **Frozen Account:** An account state (`AccountStatus.FROZEN`) that prevents the owner from initiating outgoing transfers. Incoming transfers are still allowed.

## L
- **Ledger:** The immutable, chronological log of all financial movements in the system.
- **Ledger Entry:** A single row in the ledger representing one side of a transaction (either a DEBIT or a CREDIT).

## S
- **Service:** A Python function in `services.py` responsible for complex business logic and database *writes*.
- **Selector:** A Python function in `selectors.py` responsible for complex database *reads*.

## T
- **Transaction:** The header record of a money movement. It groups multiple `LedgerEntry` records together under a single `reference` ID.
- **Transfer:** The user-facing *action* of moving money from one account to another. A successful transfer creates one Transaction and two Ledger Entries.
