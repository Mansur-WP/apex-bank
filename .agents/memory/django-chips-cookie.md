---
name: Django CHIPS cookie fix
description: How to make Django session cookies work inside cross-origin iframes (Replit preview pane) using CHIPS and CSRF_USE_SESSIONS.
---

## The rule
Two changes are required together:

1. `CSRF_USE_SESSIONS = True` — stores CSRF token server-side in the session; eliminates the separate `csrftoken` cookie which Django 5.2 cannot stamp with Partitioned natively.
2. Custom `PartitionedCookiesMiddleware` — monkey-patches Python's cookie library so it can render the `Partitioned` flag, then stamps the session cookie.

## The monkey-patch (BOTH lines required)
```python
from http.cookies import Morsel
Morsel._reserved["partitioned"] = "Partitioned"  # registers the attribute name
Morsel._flags.add("partitioned")                  # marks it as a boolean flag (no "=True")
```
Without `_flags`, Python renders `Partitioned=True` which is invalid. With only `_flags` missing, the attribute appears with a value instead of as a bare word.

## Middleware ordering
`PartitionedCookiesMiddleware` must be listed **before** `SessionMiddleware` in `MIDDLEWARE`. Django processes responses in reverse list order, so being first in the list means it runs last on responses — after `SessionMiddleware` has already written the `Set-Cookie` header.

## Why
Chrome 2024+ blocks all third-party cookies in cross-origin iframes — including `SameSite=None; Secure`. The CHIPS spec (`Partitioned`) creates per-top-level-site cookie partitions that are exempt from this block. Django 5.2's CSRF middleware has no native Partitioned support for the CSRF cookie, hence using sessions instead.

## Session cookie settings
```python
SESSION_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_PARTITIONED = True  # Django 5.1+ native; middleware also enforces it
```
