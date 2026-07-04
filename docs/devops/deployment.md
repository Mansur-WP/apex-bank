# 🚀 Apex Bank — Production Deployment Guide

> **Document Owner:** Lead DevOps Engineer  
> **Last Updated:** July 4, 2026  
> **Status:** Living Document  
> **Applies To:** Staging & Production Environments

---

## 1. Overview

Apex Bank uses a containerized deployment model via Docker. The production stack consists of:
- **Nginx/Cloudflare:** Reverse proxy and SSL termination
- **Gunicorn:** Python WSGI HTTP Server
- **Django:** Core application
- **PostgreSQL 15:** Primary database

---

## 2. Prerequisites

1. A Linux server (Ubuntu 22.04 recommended)
2. Docker and Docker Compose installed
3. A domain name pointed to the server
4. SendGrid/Mailgun account (for email)

---

## 3. Environment Variables

Create a `.env` file in the root directory (where `docker-compose.yml` lives).

> [!CAUTION]
> **CRITICAL SECURITY WARNING:** You MUST change the `SESSION_SECRET` and `POSTGRES_PASSWORD` values. Failure to do so will result in immediate compromise.

```bash
# Core
DEBUG=False
SESSION_SECRET=generate_a_very_long_random_string_here

# Database
DATABASE_URL=postgres://apex:your_secure_password@db:5432/apex_bank
POSTGRES_USER=apex
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=apex_bank

# Security (Crucial for CSRF and allowed hosts)
APP_CSRF_TRUSTED_ORIGINS=https://app.apexbank.com
ALLOWED_HOSTS=app.apexbank.com,www.apexbank.com

# Email (Future Phases)
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your_sendgrid_key
```

---

## 4. Deployment Steps

### 4.1 First-time Setup

1. **Clone the repository onto the server.**
2. **Create the `.env` file as shown above.**
3. **Build and start the containers:**
   ```bash
   docker-compose up -d --build
   ```
4. **Run database migrations:**
   ```bash
   docker-compose exec web python manage.py migrate
   ```
5. **Create a superuser:**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

### 4.2 Updating to a New Version

To deploy new code changes without downtime:

```bash
git pull origin main
docker-compose up -d --build
docker-compose exec web python manage.py migrate
```

---

## 5. Security Hardening Check

Before going live, verify:
- `DEBUG=False` in `.env`
- The `SESSION_SECRET` is set and complex.
- `SECURE_SSL_REDIRECT = True` is uncommented in `settings.py` (if SSL is active).
- `SESSION_COOKIE_SECURE = True` is uncommented in `settings.py`.

---

## 6. Reverse Proxy Configuration (Nginx)

Nginx should sit in front of Docker to handle SSL. Example config:

```nginx
server {
    listen 80;
    server_name app.apexbank.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name app.apexbank.com;

    ssl_certificate /etc/letsencrypt/live/app.apexbank.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.apexbank.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/apex-bank/banking/staticfiles/;
    }
}
```
