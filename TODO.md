# TODO - Phase 6: Admin Dashboard and Banking Operations

- [ ] Update `bank_accounts.models.Account` to include `status` with choices (ACTIVE/FROZEN)
- [ ] Add migration for the new `status` field
- [ ] Enforce business rule: frozen accounts cannot transfer (`transfers.services.execute_transfer`)
- [ ] Update transfer UI to show a friendly error when sender is frozen (`transfers.views.TransferView`)
- [ ] Add admin-only operations to freeze/unfreeze accounts with strict permission checks
- [ ] Extend `/admin-dashboard/` backend context to include:
  - [ ] total users/accounts/transactions/total money in system
  - [ ] analytics: highest balance, average balance, total transfers
  - [ ] transaction monitoring rows
  - [ ] search for users/accounts/transactions
- [ ] Update `accounts/admin_dashboard.html` to add:
  - [ ] user management table
  - [ ] account status actions + display
  - [ ] transaction monitoring table
  - [ ] search UI + results
  - [ ] analytics section
- [ ] Add/adjust tests for:
  - [ ] frozen can login
  - [ ] frozen cannot transfer
  - [ ] admin can freeze/unfreeze and non-admin cannot
  - [ ] admin search returns expected results
- [ ] Run `makemigrations`, `migrate`, and `test`

