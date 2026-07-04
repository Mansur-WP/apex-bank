# Contributing to Apex Bank

First off, thank you for considering contributing to Apex Bank! This project serves as an educational sandbox for production-grade fintech engineering patterns in Django.

## Development Setup

1. **Clone the repository**
2. **Create a virtual environment:** `python -m venv .venv`
3. **Activate the environment:**
   - Windows: `.venv\Scripts\activate`
   - Unix/macOS: `source .venv/bin/activate`
4. **Install dependencies:** `pip install -r banking/requirements.txt`
5. **Run migrations:** `python banking/manage.py migrate`
6. **Start the server:** `python banking/manage.py runserver` (or use the provided `run-dev.ps1` script on Windows)

## Coding Standards

### 1. The "Why / What / How" Docstring Pattern
All models, services, forms, and significant modules must follow this standard docstring pattern:

```python
"""
Why it exists:
    Brief explanation of the problem this code solves.

What it does:
    High-level description of the functionality.

How it connects:
    Relationships to other parts of the system.
"""
```

### 2. Architecture: Service / Selector Pattern
- **Do not** put business logic in views or models.
- **Write Operations:** Place in `services.py`. Must use `transaction.atomic()`.
- **Read Operations:** Place complex queries in `selectors.py`.

### 3. Financial Integrity
- Every transfer must use `select_for_update()` to prevent race conditions.
- Every transfer must generate exactly two `LedgerEntry` records (Double-Entry).

## Submitting Pull Requests

1. Fork the repository and create your branch from `main`.
2. Write tests for your new feature (especially if it involves `transfers/`).
3. Ensure all tests pass: `python banking/manage.py test banking`
4. Update relevant documentation in the `docs/` directory.
5. Submit the PR with a clear description of the problem solved.
