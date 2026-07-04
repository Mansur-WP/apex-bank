# 🗺️ Apex Bank — User Flows Specification

> **Document Owner:** Product Manager / UX Designer  
> **Last Updated:** July 4, 2026

---

## 1. Authentication Flows

### 1.1 Registration Flow
1. User navigates to `/accounts/register/`.
2. Form presented: First Name, Last Name, Email, Password, Confirm Password.
3. User submits form.
4. **Validation:** Checks email uniqueness, password match, and password strength.
5. **System Action:** Creates `CustomUser` -> triggers signal -> creates `Account` with auto-generated 10-digit number and ₦10,000 balance.
6. **Success:** User is automatically logged in and redirected to `/dashboard/`.

### 1.2 Login Flow
1. User navigates to `/accounts/login/`.
2. Form presented: Email, Password.
3. User submits form.
4. **Success:** Redirect to `/dashboard/` (or `?next=` parameter URL).
5. **Failure:** Re-renders form with generic "Invalid email or password" message.

---

## 2. Core Banking Flows

### 2.1 P2P Transfer Flow (Happy Path)
1. User navigates to `/transfers/` (Send Money).
2. User enters Recipient Account Number (10 digits).
3. **Async Action:** Frontend fires `GET /transfers/verify-recipient/?account_number=X`.
4. **UI Update:** "Recipient: Jane Doe" appears below the input.
5. User enters Amount and optional Note.
6. User clicks "Send Money".
7. **System Action:** Validates balance, locks rows, generates transaction/ledger records.
8. **Success:** Redirects to `/dashboard/` with flash message: "Successfully sent ₦X to Jane Doe".

### 2.2 Transfer Validation Failures
If the transfer fails business logic validation (e.g., insufficient funds, frozen account, negative amount), the system redirects back to `/transfers/` with a red flash message explaining the error.

### 2.3 Transaction History Flow
1. User navigates to `/transfers/history/`.
2. System displays paginated list (15 per page) of all sent and received transactions.
3. User clicks on a specific Transaction Reference (`TXN-123...`).
4. System routes to `/transfers/transactions/<ref>/` displaying the detailed receipt.

---

## 3. Admin Operations

### 3.1 Freeze Account Flow
1. Staff member navigates to `/admin-dashboard/accounts/`.
2. Staff member locates suspicious account and clicks "Freeze".
3. System posts to `/accounts/freeze/` with the target `account_number`.
4. **System Action:** Service sets `Account.status = FROZEN` and mirrors to `CustomUser.is_frozen`.
5. **Success:** Redirects back to dashboard with success flash message.

### 3.2 Ledger Audit Flow
1. Staff member navigates to `/transfers/ledger-audit/`.
2. System displays unpaginated chronological list of all DEBIT/CREDIT entries across the entire system.
3. Used for manual reconciliation and fraud investigation.
