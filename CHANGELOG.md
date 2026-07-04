# Changelog

All notable changes to Apex Bank will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - Phase 8-12 Planned
### Added
- Phase 8: Audit trails and structured logging
- Phase 9: Real-time notifications and email receipts
- Phase 10: Django REST Framework API
- Phase 11: Fraud detection and transaction monitoring
- Phase 12: PDF statement generation

## [0.1.0] - 2026-07-04
### Added (Phase 7: The Ledger & Admin Phase)
- **Double-Entry Ledger Engine:** Implemented `LedgerEntry` model enforcing strict conservation of money via `execute_transfer()`.
- **Admin Action Service:** Added `freeze_account` and `unfreeze_account` logic synchronizing `Account.status` with `CustomUser.is_frozen`.
- **Admin Dashboard:** Created staff-only views for monitoring users, accounts, transactions, and system-wide ledger activity.
- **My Ledger View:** Added customer-facing ledger view showing DEBIT/CREDIT line items.
- **Account Statement View:** Added monthly/weekly aggregation statements.

### Added (Phases 1-6: Foundation)
- **Identity System:** Custom User model (`CustomUser`) using email for authentication.
- **Account Generation:** Automatic provisioning of 10-digit account numbers on registration.
- **Atomic Transfers:** Service layer with row-level locking (`select_for_update()`) preventing race conditions and deadlocks.
- **Dashboard Interface:** Core web UI with Bootstrap Icons and Chart.js integration.
- **Testing Suite:** Comprehensive edge-case testing for transfer validation and money conservation.
