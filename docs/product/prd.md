# 📄 Apex Bank — Product Requirements Document (PRD)

> **Document Owner:** Product Manager  
> **Last Updated:** July 4, 2026  
> **Status:** Living Document  
> **Version:** 1.0 (Phases 1–7)

---

## 1. Executive Summary

Apex Bank is a digital banking simulator built to demonstrate production-grade fintech engineering patterns (e.g., double-entry ledgers, atomic transactions, row-level locking). 

While it is an educational/portfolio project, it is treated as a real product to model the exact problems faced by actual neobanks (e.g., Monzo, Kuda, Revolut).

### 1.1 Vision
To provide a secure, reliable, and auditable digital wallet experience that ensures 100% financial data integrity.

### 1.2 Problem Statement
Building financial software is difficult. Race conditions, deadlocks, and rounding errors can destroy a company. Apex Bank serves as a technical sandbox to solve these problems elegantly using Django.

---

## 2. Target Users & Personas

### 2.1 Persona 1: The Retail Customer ("Alice")
- **Goal:** Wants to send money instantly to friends or family.
- **Pain Point:** Hates complex registration forms and delayed transfers.
- **Needs:** A clean dashboard, instant transfer confirmation, and a clear transaction history.

### 2.2 Persona 2: The Bank Administrator ("Bob")
- **Goal:** Manage platform security and resolve customer disputes.
- **Pain Point:** Lacks visibility into the underlying financial ledger.
- **Needs:** Ability to view system-wide ledgers, monitor suspicious activity, and freeze accounts if fraud is suspected.

---

## 3. User Journeys

### 3.1 Onboarding
1. User visits landing page.
2. User enters name, email, and strong password.
3. System automatically provisions a 10-digit account number.
4. System grants a ₦10,000 "welcome bonus" (for simulation purposes).
5. User is logged in and redirected to the Dashboard.

### 3.2 Peer-to-Peer Transfer
1. User clicks "Send Money".
2. User enters recipient's 10-digit account number.
3. System asynchronously verifies the account and displays the recipient's name.
4. User enters amount and optional note.
5. User clicks "Send".
6. System processes transfer atomically and updates balances.
7. User sees success message and updated balance.

### 3.3 Account Freeze (Admin)
1. Staff member logs into Admin Dashboard.
2. Staff member looks up a suspicious account.
3. Staff member clicks "Freeze".
4. System updates account status.
5. Target user is blocked from sending money (but can still log in and view history).

---

## 4. MVP Scope (Completed Phases 1–7)

| Feature Area | Features | Status |
|---|---|---|
| **Identity** | Email registration, login, logout, profile view, password change | ✅ Done |
| **Accounts** | Auto-generation of 10-digit account numbers, balance display | ✅ Done |
| **Transfers** | Wallet-to-wallet transfers, asynchronous recipient verification | ✅ Done |
| **Ledger** | Double-entry tracking (DEBIT/CREDIT records for every transfer) | ✅ Done |
| **History** | Paginated transaction lists, detailed receipt view | ✅ Done |
| **Statements** | Monthly/weekly aggregation, income/expense summaries | ✅ Done |
| **Admin** | Dashboard charts, user listing, ledger audit, freeze/unfreeze | ✅ Done |

---

## 5. Roadmap (Future Phases)

| Phase | Description | Key Deliverables |
|---|---|---|
| **Phase 8** | Audit Trails | User activity logging, admin action logs, login history |
| **Phase 9** | Notifications | In-app alerts, email notifications on transfer receipt |
| **Phase 10** | REST API | Django REST Framework integration, JWT auth, mobile readiness |
| **Phase 11** | Fraud Detection | Rules engine (e.g., flag large transfers, rapid sequential transfers) |
| **Phase 12** | Export & Reporting | Download statements as CSV/PDF |

---

## 6. Success Metrics (KPIs)

For a simulator, "success" is technical stability rather than revenue.

1. **Conservation Error Rate:** 0.00% (Total debits must exactly equal total credits).
2. **Transfer Success Rate:** > 99.9% (excluding user errors like insufficient funds).
3. **Lock Contention Rate:** < 1% of transactions experiencing database deadlocks under load.
4. **Test Coverage:** > 90% across models, views, and services.
