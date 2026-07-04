# 🔌 Apex Bank — API Specification

> **Document Owner:** Principal Solutions Architect  
> **Last Updated:** July 4, 2026  
> **Status:** Living Document  
> **Version:** 1.0 (Phase 7)

---

## 1. Overview

Apex Bank is primarily a server-rendered Django application. However, it exposes a minimal JSON API for client-side interactivity (e.g., verifying a recipient before initiating a transfer).

This document outlines the current internal API and serves as a foundation for the planned **Phase 10: REST API** expansion.

---

## 2. Current Internal API

The following endpoints are currently used by the frontend via asynchronous fetch requests.

### 2.1 Verify Recipient

**Endpoint:** `GET /transfers/verify-recipient/`  
**Description:** Verifies if a given account number exists and returns the account holder's name. This is used by the frontend JS to show the recipient's name before the user confirms a transfer.  
**Authentication Required:** Yes (Session Cookie)

#### Request

**Query Parameters:**
- `account_number` (string, required): The 10-digit account number to verify.

**Example Request:**
```http
GET /transfers/verify-recipient/?account_number=1234567890 HTTP/1.1
Host: apexbank.local
Cookie: sessionid=...
```

#### Responses

**Success (200 OK):**
```json
{
  "valid": true,
  "name": "Jane Doe"
}
```

**Invalid/Not Found (404 Not Found):**
```json
{
  "valid": false,
  "error": "Account not found"
}
```

**Missing Parameter (400 Bad Request):**
```json
{
  "valid": false,
  "error": "Account number is required"
}
```

**Unauthorized (403 Forbidden / 302 Redirect):**
Returns a redirect to the login page or a 403 if not authenticated.

---

## 3. Future REST API Specification (Phase 10 Draft)

The Phase 10 REST API will use **Django REST Framework (DRF)**.

### 3.1 Authentication Strategy

- **Primary:** JWT (JSON Web Tokens) via `djangorestframework-simplejwt`
- **Fallback:** Session authentication (for requests originating from the web UI)

### 3.2 Standard Response Envelope

All API responses will use a standard envelope for consistency:

**Success:**
```json
{
  "status": "success",
  "data": { ... }
}
```

**Error:**
```json
{
  "status": "error",
  "error_code": "ERR_INSUFFICIENT_FUNDS",
  "message": "Sender account has insufficient funds.",
  "details": {
    "current_balance": "500.00",
    "requested_amount": "1000.00"
  }
}
```

### 3.3 Proposed Endpoints

#### Authentication

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/auth/token/` | Obtain JWT access/refresh tokens |
| `POST` | `/api/v1/auth/refresh/` | Refresh JWT access token |
| `POST` | `/api/v1/auth/register/` | Register a new user account |

#### Wallet & Transfers

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/wallet/balance/` | Get current account balance |
| `POST` | `/api/v1/wallet/transfers/` | Initiate a money transfer |
| `GET` | `/api/v1/wallet/transfers/` | List transaction history (paginated) |
| `GET` | `/api/v1/wallet/transfers/{ref}/` | Get details of a specific transaction |
| `GET` | `/api/v1/wallet/statement/` | Generate account statement summary |

#### Webhooks (Future)

To support integration with third-party providers (e.g., payment gateways in Phase 6), the system will need to accept incoming webhooks.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/webhooks/paystack/` | Handle Paystack event notifications |

---

## 4. Rate Limiting (Required for API)

Before releasing the API, rate limits must be strictly enforced:

- **Token issuance (`/auth/token/`):** 5 requests per minute per IP
- **Registration (`/auth/register/`):** 3 requests per hour per IP
- **Verify Recipient (`/verify-recipient/`):** 60 requests per hour per user
- **Transfers (`/transfers/`):** 20 requests per hour per user

*See the [Security Threat Model](../security/threat-model.md) for more details on rate limiting implementation.*
