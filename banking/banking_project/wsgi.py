"""
wsgi.py — WSGI entry point for the banking simulator.

Why it exists:
    WSGI (Web Server Gateway Interface) is the standard Python interface
    between web servers (gunicorn, uWSGI, etc.) and Django applications.
    Production deployments use this file.

What it does:
    Exposes the `application` callable that any WSGI-compatible server
    can call to handle HTTP requests.

How it connects:
    References banking_project.settings via DJANGO_SETTINGS_MODULE.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "banking_project.settings")

application = get_wsgi_application()
