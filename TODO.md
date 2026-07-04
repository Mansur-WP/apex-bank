# Apex Bank — Freeze/Unfreeze System (end-to-end)

## Plan checklist
- [ ] Fix transfer protection: sender frozen blocks outgoing only; receiver frozen allowed.
- [ ] Align admin freeze/unfreeze actions to use `bank_accounts.Account.status` as canonical.
- [ ] Optionally mirror `CustomUser.is_frozen` from `Account.status` for consistency.
- [ ] Ensure freeze/unfreeze URLs are wired into the admin area routes.
- [ ] Implement admin_dashboard freeze/unfreeze forms (CSRF + account_number; correct URL targets).
- [ ] Update admin_users page to show status badge and add freeze/unfreeze actions per user.
- [ ] Add tests:
  - [ ] freeze account (staff) updates status
  - [ ] unfreeze account (staff) updates status
  - [ ] frozen sender blocked
  - [ ] frozen receiver allowed
  - [ ] non-staff denied freeze/unfreeze
- [ ] Run full test suite and fix any failures.

