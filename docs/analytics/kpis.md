# 📊 Apex Bank — Analytics & KPIs

> **Document Owner:** Product Manager  
> **Last Updated:** July 4, 2026

---

## 1. Overview

While Apex Bank is a simulator, it includes a staff-only Admin Dashboard designed to track business health and system activity. This document defines the key performance indicators (KPIs) monitored by the system.

---

## 2. Dashboard Metrics (Current)

The current `/admin-dashboard/` displays the following real-time metrics:

1. **Total Users:** Count of `CustomUser` where `is_superuser=False`.
2. **Total Transfers:** Count of all `Transaction` records.
3. **Total Ledger Volume:** Sum of all `amount` values across `LedgerEntry` records where `entry_type=CREDIT`.
4. **Frozen Accounts:** Count of `Account` records where `status=FROZEN`.

---

## 3. Product KPIs (Future Phases)

To simulate a real fintech growth model, we plan to implement the following event tracking and funnel analysis.

### 3.1 Acquisition & Activation
- **Sign-up Conversion Rate:** Visitors to `/accounts/register/` vs Completed Registrations.
- **Time to First Transfer (TTFT):** Average time between registration timestamp and first outbound `Transaction` timestamp.
- **Active Wallets (MAU):** Accounts with at least one transaction in the last 30 days.

### 3.2 Financial Velocity
- **Daily Transaction Volume (DTV):** Total ₦ moved per day.
- **Average Transaction Value (ATV):** `Total Volume / Total Transactions`.
- **System Float:** Total sum of all `Account.balance` across the system (simulating deposits held by the bank).

### 3.3 System Health Metrics
- **Conservation Check Failures:** Tracked via Sentry (should always be 0).
- **Deadlock Occurrences:** Tracked via Sentry.
- **Failed Transfer Rate:** Percentage of initiated transfers that fail due to insufficient funds or frozen status. High rates may indicate bad UX or fraud attempts.

---

## 4. Admin Charts (Current)

The dashboard uses Chart.js to visualize:

- **Transaction Volume over Time:** A line chart plotting the number of transactions per day over the last 30 days.
- **User Growth:** A bar chart plotting new registrations per week.

*Note: Data for these charts is currently passed directly from `AdminDashboardView.get_context_data()` to the template context.*
