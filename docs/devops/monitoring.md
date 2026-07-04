# 📈 Apex Bank — Monitoring & Logging Strategy

> **Document Owner:** Lead DevOps Engineer  
> **Last Updated:** July 4, 2026  
> **Status:** Draft (Phase 8 Implementation)

---

## 1. Overview

Visibility into system behavior is critical for a banking application. This document outlines the planned monitoring stack and logging taxonomy for production.

---

## 2. Infrastructure Monitoring (Prometheus/Grafana)

To be implemented via node_exporter and cAdvisor.

**Key Metrics to Track:**
- Server CPU / Memory / Disk usage
- PostgreSQL connection pool exhaustion
- PostgreSQL slow queries (> 500ms)
- Gunicorn worker saturation

---

## 3. Application Performance Monitoring (APM)

We will use **Sentry** for APM and exception tracking.

**Configuration requirements:**
- Only enabled when `DEBUG=False`.
- Filter sensitive PII (passwords, session cookies, CSRF tokens) via Sentry's data scrubber before transmission.
- Track transaction execution time (`transfers/services.py`). If `execute_transfer()` regularly takes > 100ms, database locking may be causing contention.

---

## 4. Structured Audit Logging

Django's default logging is insufficient for financial audits. We will implement structured JSON logging using `python-json-logger`.

### 4.1 Log Taxonomy

| Event Code | Trigger | Log Level | Included Data |
|---|---|---|---|
| `AUTH.001` | Successful Login | INFO | email, ip_address |
| `AUTH.002` | Failed Login | WARN | email, ip_address |
| `TXN.001` | Transfer Initiated | INFO | reference, sender, receiver, amount |
| `TXN.002` | Transfer Failed (Validation) | WARN | sender, reason |
| `TXN.003` | Transfer Failed (Conservation) | CRITICAL | reference, debit_total, credit_total |
| `ADM.001` | Account Frozen | INFO | acting_admin, target_account |

### 4.2 Django Logging Configuration (settings.py snippet)

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': '/var/log/apex/audit.log',
            'when': 'midnight',
            'formatter': 'json',
        },
    },
    'loggers': {
        'apex.audit': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
    },
}
```

---

## 5. Health Checks

A public, unauthenticated health check endpoint must be exposed for load balancers.

**Endpoint:** `GET /health/`

**Checks performed:**
1. Database connectivity (`SELECT 1`)
2. Cache connectivity

**Response:**
```json
{
    "status": "healthy",
    "db": "connected",
    "timestamp": "2026-07-04T12:00:00Z"
}
```
