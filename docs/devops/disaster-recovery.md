# 🚨 Apex Bank — Disaster Recovery Plan

> **Document Owner:** Lead DevOps Engineer  
> **Last Updated:** July 4, 2026  
> **Status:** Draft

---

## 1. Overview

Because Apex Bank operates a financial ledger, data loss is catastrophic. This Disaster Recovery (DR) plan outlines backup procedures, Recovery Point Objectives (RPO), and Recovery Time Objectives (RTO).

---

## 2. Recovery Objectives

| Metric | Target | Definition |
|---|---|---|
| **RPO** (Recovery Point Objective) | 0 seconds | No committed transactions can be lost. |
| **RTO** (Recovery Time Objective) | < 15 minutes | Maximum downtime during a full restore. |

---

## 3. Database Backup Strategy

To achieve 0-second RPO, we rely on **PostgreSQL Continuous Archiving (WAL logging)** alongside daily base backups.

### 3.1 Daily Base Backups

A cron job runs nightly to dump the entire database and push it to AWS S3.

```bash
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
docker-compose exec -t db pg_dump -U apex -F c apex_bank > /backups/apex_bank_$TIMESTAMP.dump
aws s3 cp /backups/apex_bank_$TIMESTAMP.dump s3://apex-bank-backups/daily/
```

### 3.2 Continuous Archiving (WAL)

Write-Ahead Logs (WAL) record every single change to the database before it is committed. We use `pgbackrest` or `wal-g` to stream WAL files to S3 continuously.

If the primary database crashes, we restore the last daily base backup and replay the WAL files up to the exact moment of failure.

---

## 4. Disaster Scenarios & Playbooks

### Scenario 1: Server Hardware Failure (Complete Loss)

**Severity:** Critical
**Action Plan:**
1. Provision a new server instance via Terraform.
2. Pull `docker-compose.yml` and `.env` from secure secrets manager.
3. Start the containers (`docker-compose up -d db`).
4. Pull the latest daily backup from S3.
5. Restore the database: `pg_restore -d apex_bank latest.dump`.
6. Apply WAL logs to recover transactions since the last backup.
7. Start the `web` application container.
8. Update DNS / Load Balancer to point to the new server IP.

### Scenario 2: Administrator Accidentally Deletes Data

**Severity:** Critical
**Action Plan:**
Since `Transaction` and `LedgerEntry` models use `PROTECT`, accidental deletion from the admin panel is blocked. However, if a developer runs a destructive raw SQL query:
1. Immediately take the application offline to prevent further state changes.
2. Perform a Point-In-Time Recovery (PITR) using WAL logs to restore the database to 1 second before the destructive query was run.

### Scenario 3: Double-Entry Ledger Imbalance Detected

**Severity:** Catastrophic
**Action Plan:**
If the reconciliation query (see Ledger Specification) returns mismatched balances:
1. Trigger Maintenance Mode immediately.
2. Investigate application logs to find the exact transaction that violated conservation.
3. If the bug is identified, write a one-off database migration script to manually post the missing ledger entries. Do NOT attempt to fix balances directly; always fix via Ledger Entries.

---

## 5. Security of Backups

- All backups stored in S3 must use **AES-256 encryption at rest**.
- S3 buckets must be configured with **Object Lock** (WORM - Write Once, Read Many) to prevent ransomware from encrypting or deleting backups.
- AWS credentials used for backups must only have `s3:PutObject` permissions (no delete access).
