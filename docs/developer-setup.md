# Developer Setup

This document explains how to set up a development environment for Synch-Manager.

## 1. Requirements

- Git
- Docker and Docker Compose
- Python 3.11+
- Node.js 20+ and npm or yarn (optional if using only Docker)

## 2. Backend Development

### 2.1 Local Python Environment (optional)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run Django locally (without Docker):

```bash
export DJANGO_SETTINGS_MODULE=config.settings
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### 2.2 Docker-based Backend

From the repo root:

```bash
docker-compose up -d mariadb timescaledb redis
docker-compose up -d web
```

Run migrations:

```bash
docker-compose run --rm web python manage.py migrate
```

Run tests:

```bash
docker-compose run --rm web python manage.py test
```

## 3. Frontend Development

From `frontend/`:

```bash
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

The React dev server will be available at `http://localhost:5173`.

## 4. Coding Guidelines

- Use feature branches: `feature/<module>-<description>`.
- Open pull requests against `main`.
- Write tests for new features.
- Follow Django and DRF best practices:
  - Use viewsets and routers for REST endpoints.
  - Keep business logic in services or tasks, not in views.
- For React:
  - Use functional components and hooks.
  - Keep API calls in `src/api/client.ts` and module-specific helpers.

## 5. Seed Data

The `scripts/seed_data.py` script (to be implemented) will insert:

- Sample users and roles.
- A small set of network elements.
- Test alarms and performance data.

Run seed script:

```bash
docker-compose run --rm web python scripts/seed_data.py
```

## 6. Next Steps

Development will proceed module by module:

1. Fault Management (alarms, traps, viewer).
2. Inventory (NE registry and discovery).
3. Configuration (policies and audits).
4. Performance (metrics and charts).
5. Security (RBAC, audit log).
6. PTP (client management and LinuxPTP integration).
