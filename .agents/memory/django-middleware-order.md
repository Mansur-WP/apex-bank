---
name: Django middleware response order
description: Django processes middleware in REVERSE list order for responses — first in list = last on response.
---

## The rule
Django's `__call__`-based middleware wraps the chain: the first middleware in the list is the outermost wrapper, so it processes requests first but responses last.

**Request order**: top → bottom (index 0 first)
**Response order**: bottom → top (index 0 last)

## How to apply
Any middleware that needs to modify a response header/cookie that was SET by another middleware must be listed BEFORE that middleware.

Example: `PartitionedCookiesMiddleware` needs to modify the `sessionid` cookie AFTER `SessionMiddleware` sets it. So it must be placed before `SessionMiddleware` in the list, which means it runs after SessionMiddleware in response processing.

```python
MIDDLEWARE = [
    "banking_project.middleware.PartitionedCookiesMiddleware",  # runs LAST on response
    "django.contrib.sessions.middleware.SessionMiddleware",      # runs SECOND-to-last
    ...
]
```

**Why:** If PartitionedCookiesMiddleware is listed after SessionMiddleware, it runs before it on the response and tries to modify a cookie that doesn't exist yet.
