# S.A.M Blocks Inventory — Project Walkthrough

## 1. Project Overview
This is a full-featured inventory and sales management system for S.A.M Blocks, built with Flask (Python). It supports both SQLite (local) and PostgreSQL (production), and is ready for deployment on Docker, Render, Railway, Fly.io, or a Linux server.

## 2. File-by-File Explanation

### app.py
- Main Flask application.
- Handles all routes, authentication, admin/customer logic, database connections, migrations, and audit logging.
- Supports both SQLite and Postgres via environment variables (`FORCE_SQLITE`, `DATABASE_URL`).
- Contains all business logic for products, orders, payments, trips, audits, and reconciliation.

### templates/
- Contains all HTML pages (Jinja2 templates).
- Each route in `app.py` renders a template. Example mappings:
  - `/` → `index.html` (dashboard)
  - `/login` → `auth/login.html`
  - `/register` → `auth/register.html`
  - `/products` → `products.html`
  - `/orders_list` → `orders_list.html`
  - `/trips` → `trips.html`
  - `/trips/edit/<id>` → `trips_edit.html`
  - `/admin/*` → `admin/` subfolder templates (admin dashboard, audit, products, etc.)
- `base.html` is the main layout, used by all other templates.

### static/
- Contains static assets (CSS, images).
- `style.css`: main stylesheet for the UI.
- `sam.jpg`: logo image.

### requirements.txt
- Lists all Python dependencies (Flask, flask-login, werkzeug, psycopg2-binary, etc.).

### Dockerfile
- Builds a production-ready Docker image for the app.
- Installs system and Python dependencies, copies code, exposes port 5000, runs Gunicorn.

### docker-compose.yml
- Defines a multi-container setup (app + Postgres) for local development/testing.

### Procfile
- Used by platforms like Render/Railway to run Gunicorn with the correct port.

### render.yaml
- Manifest for Render deployments (uses Docker build).

### migrate_sqlite_to_postgres.py
- Script to migrate your local SQLite database to Postgres, preserving IDs and audit history.
- Usage: see README.md for command examples.

### schema.sql / schema_pg.sql
- Database schema files for SQLite and Postgres.
- Used to initialize the database tables.

### deploy/
- Contains deployment helper scripts and config templates:
  - `deploy_gunicorn.sh`: automates server setup (clone, venv, install, init-db, systemd/nginx install).
  - `sam_blocks.service`: systemd unit for Gunicorn.
  - `nginx_sam_blocks.conf`: nginx config for reverse proxy/static serving.
  - `README_DEPLOY.md`: step-by-step server deployment instructions.

### tests/
- Contains test scripts (e.g., `test_auth_order.py`) for authentication/order logic.

### README.md
- Main documentation: setup, deployment, migration, troubleshooting, and platform-specific instructions.

## 3. Key Features
- User registration/login with roles (admin/customer).
- Admin dashboard: manage products, orders, trips, audits, reconciliation, breakages.
- Customer dashboard: view products, place orders, see payments/orders.
- Audit logging for transparency (all changes tracked).
- CSV import/export for products.
- Migration script to move from SQLite to Postgres.
- Ready for deployment on Docker, Render, Railway, Fly.io, or server.

## 4. Deployment & Migration
- Local: run with SQLite (see README.md for quick start).
- Docker: use Dockerfile and docker-compose.yml for containerized setup.
- Render/Railway/Fly.io: connect repo, set environment variables (`FORCE_SQLITE=1` for SQLite, `DATABASE_URL` for Postgres), deploy.
- Migration: run `migrate_sqlite_to_postgres.py` to copy data from SQLite to Postgres.

## 5. Route-to-Template Mapping
| Route                | Template                  | Purpose                       |
|----------------------|--------------------------|-------------------------------|
| `/`                  | index.html               | Dashboard/home                |
| `/login`             | auth/login.html          | Login page                    |
| `/register`          | auth/register.html       | Registration page             |
| `/products`          | products.html            | Product list                  |
| `/orders_list`       | orders_list.html         | Orders overview               |
| `/orders_add`        | orders_add.html          | Add new order                 |
| `/payments_list`     | payments_list.html       | Payments overview             |
| `/trips`             | trips.html               | Trip management               |
| `/trips/edit/<id>`   | trips_edit.html          | Edit trip                     |
| `/notes`             | notes.html               | Notes                         |
| `/customer_dashboard`| customer_dashboard.html  | Customer dashboard            |
| `/admin/*`           | admin/*.html             | Admin features (see folder)   |

## 6. How to Use/Present
- Show the README.md for setup and deployment steps.
- Walk through `app.py` for route logic and feature implementation.
- Open templates/ for UI pages and explain how each route renders a template.
- Use the migration script and deployment files to demonstrate production readiness.
- Highlight audit logging and admin/customer separation for transparency and security.

---

**You can print this file or convert it to PDF for your supervisors.**
If you need more detail on any file or feature, let me know!