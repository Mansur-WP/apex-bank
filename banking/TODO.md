Phase 7 — Double-Entry Ledger System

✅ LedgerEntry model exists (transfers/models.py + migration).
✅ execute_transfer() creates Transaction + DEBIT + CREDIT ledger entries in transaction.atomic().
✅ Double-entry conservation check (debits == credits) exists.

🔶 UI/Access control work
- [ ] Add ledger views (admin audit + user scoped) (views/views_ledger.py)
- [ ] Add routes for /transfers/ledger/ and /transfers/ledger-audit/
- [ ] Add templates to render ledger entries table
- [x] Add/extend tests to verify user/admin visibility and that transfers create ledger entries


