#!/usr/bin/env python
"""
manage.py — Django's command-line utility for administrative tasks.

Why it exists:
    Django requires this entry point to run management commands such as
    runserver, migrate, createsuperuser, etc.

What it does:
    Sets the DJANGO_SETTINGS_MODULE environment variable so every Django
    command knows which settings file to use, then delegates to Django's
    built-in management command runner.

How it connects:
    Points at banking_project.settings — the central configuration module
    for the entire project.
"""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "banking_project.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
