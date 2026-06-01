"""
middleware.py — Custom middleware for Apex.

PartitionedCookiesMiddleware
    Adds the `Partitioned` cookie attribute (CHIPS spec) to the session
    cookie so the app works inside cross-origin iframes (Replit preview pane).

    Why this is needed
    ------------------
    Chrome 2024+ blocks all third-party cookies in cross-origin iframes —
    including SameSite=None; Secure. The CHIPS fix marks cookies as
    `Partitioned`, meaning each top-level site gets its own isolated copy.
    This exempts them from third-party cookie blocking.

    How it works
    ------------
    Python's http.cookies.Morsel doesn't know about `Partitioned` by default.
    We monkey-patch the class-level _reserved dict and _flags set once at
    import time so every Morsel instance created anywhere in this process
    can hold and render the attribute correctly.

    Middleware ordering (important!)
    --------------------------------
    This middleware must be listed BEFORE SessionMiddleware in MIDDLEWARE.
    Django processes responses in reverse order, so placing it first means
    it runs last on responses — after SessionMiddleware has already written
    the Set-Cookie header. That lets us stamp Partitioned onto the cookie
    after it exists.
"""

from http.cookies import Morsel

# ── One-time monkey-patch of Python's cookie library ─────────────────────────
# _reserved maps the dict key to the Set-Cookie attribute name.
# _flags is the set of boolean attributes (output as bare word, no "=value").
if "partitioned" not in Morsel._reserved:
    Morsel._reserved["partitioned"] = "Partitioned"
if "partitioned" not in Morsel._flags:
    Morsel._flags.add("partitioned")


# This middleware is intentionally left blank to remove Replit/iframe
# coupling from the codebase. It should not be enabled in settings.

class PartitionedCookiesMiddleware:
    """(deprecated) Previously stamped session cookie with Partitioned.

    This file is retained only for reference; it is intentionally not used
    by the app (it is not enabled in MIDDLEWARE).
    """


    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if "sessionid" in response.cookies:
            morsel = response.cookies["sessionid"]
            morsel["samesite"] = "None"
            morsel["secure"] = True
            morsel["partitioned"] = True   # bare flag — no "=True"
        return response
