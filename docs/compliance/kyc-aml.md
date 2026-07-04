# ⚖️ Apex Bank — KYC & AML Compliance Specification

> **Document Owner:** Compliance & Security Officer  
> **Last Updated:** July 4, 2026  
> **Status:** Draft / Simulator Spec  
> **Region:** Nigeria (CBN Sandbox Environment)

---

## 1. Overview

As a financial simulator targeting the Nigerian banking environment, Apex Bank must model compliance with the **Central Bank of Nigeria (CBN)** regulations.

This document outlines the **Know Your Customer (KYC)** tiering system and **Anti-Money Laundering (AML)** transaction monitoring rules that will be simulated in Phase 11.

> [!CAUTION]
> This is a simulated compliance framework. A real fintech application must engage legal counsel and integrate with verified identity providers (NIMC, NIBSS) for actual compliance.

---

## 2. KYC Tier System

Currently, all Apex Bank accounts are created instantly with just an email and password (Tier 0). To simulate a real environment, we will transition to the CBN 3-Tier KYC structure.

### 2.1 Tier 0: Unverified (Current State)
- **Requirements:** Name, Email, Password.
- **Restrictions:** Cannot send money. Can only receive up to ₦10,000.
- **Status:** *Currently serves as the default state, but without restrictions. Will be restricted in Phase 11.*

### 2.2 Tier 1: Basic Verification
- **Requirements:** Tier 0 + BVN (Bank Verification Number) OR NIN (National Identity Number).
- **Daily Transaction Limit:** ₦50,000
- **Maximum Balance Limit:** ₦300,000
- **Features:** P2P Transfers, Bill Payments.

### 2.3 Tier 2: Standard Account
- **Requirements:** Tier 1 + Government ID (Passport/Driver's License) + Liveness Check (Selfie).
- **Daily Transaction Limit:** ₦200,000
- **Maximum Balance Limit:** ₦500,000
- **Features:** International Transfers.

### 2.4 Tier 3: Premium Account
- **Requirements:** Tier 2 + Proof of Address (Utility Bill) + 2FA Enabled.
- **Daily Transaction Limit:** ₦5,000,000
- **Maximum Balance Limit:** Unlimited.
- **Features:** Business features, API access.

---

## 3. AML / Fraud Detection Rules (Phase 11)

To prevent money laundering, the system will monitor transactions asynchronously. If a rule is triggered, the transaction may be flagged, delayed, or the account automatically frozen.

### 3.1 Hard Limits (Synchronous Block)
Checked before `execute_transfer` completes:
- Transfer amount exceeds KYC Tier daily limit.
- Resulting balance would exceed KYC Tier maximum balance.

### 3.2 Suspicious Activity Rules (Asynchronous Flag)
Processed via Celery after the transfer completes. These do not stop the transfer but alert the Admin dashboard.

| Rule Code | Name | Condition | Action |
|---|---|---|---|
| `AML-001` | **Rapid Velocity** | > 5 outgoing transfers in 1 hour | Flag Account (Warning) |
| `AML-002` | **Structuring (Smurfing)** | > 3 transfers just below KYC limit (e.g., ₦49,999) | Flag Account (Critical) |
| `AML-003` | **In-and-Out Sweep** | Funds received and >95% transferred out within 10 mins | Flag Transaction |
| `AML-004` | **New Account Large Transfer** | Account < 24h old sending > ₦100,000 | Freeze Account Pending Review |

### 3.3 Admin Investigation Process
1. Alert appears on Admin Dashboard.
2. Admin reviews `AML-00X` rule violation.
3. Admin investigates Ledger Audit trail.
4. Admin can either **Clear Flag** or **Freeze Account**.

---

## 4. Data Privacy (NDPA)

In compliance with the Nigeria Data Protection Act (NDPA):
- **Data Minimization:** Only collect NIN/BVN when upgrading KYC tiers.
- **Right to Erasure:** Accounts can be soft-deleted. However, `Transaction` and `LedgerEntry` records are retained for the mandatory 5-year financial audit period.
- **Encryption:** (Future) PII such as BVN/NIN must be encrypted at rest in the database.
