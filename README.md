# Synch-Manager

Open-source synchronization management system providing FCAPS management for PTP, NTP, and SyncE network elements.

Built on an entirely open-source stack: Django, React, LinuxPTP, Chrony, MariaDB, TimescaleDB, Kafka, Redis, and Grafana.

## Features

- Fault management with SNMP traps and real-time alarm viewer.
- Configuration policies and compliance audits.
- Inventory auto-discovery and NE registry.
- Performance collection (MTIE, TDEV, phase) with time-series storage.
- Security: RBAC, audit logging, JWT-based API authentication.
- PTP client management and LinuxPTP integration.
- War Mode tactical timing for mission-critical deployments.
- GNSS resilience monitoring with satellite constellation tracking.

## Quick Start (Local Docker Deployment)

### Prerequisites
- Docker Desktop 4.0+
- Docker Compose 2.0+
- 8GB RAM minimum

### One-Click Deployment

```bash
# Clone the repository
git clone https://github.com/himprapatel-rgb/synch-manager.git
cd synch-manager

# Copy environment template
cp .env.example .env

# Start all services (auto-runs migrations)
docker-compose up -d

# Create admin user (optional)
docker-compose exec web python manage.py createsuperuser
```

### Access Points

| Service | URL | Description |
|---------|-----|-------------|
| Backend API | http://localhost:8000 | Django REST API |
| API Health | http://localhost:8000/api/health/ | Health check endpoint |
| Frontend | http://localhost:5173 | React development UI |
| Grafana | http://localhost:3000 | Performance dashboards |
| API Docs | http://localhost:8000/api/docs/ | OpenAPI documentation |

## Railway Cloud Deployment

### Prerequisites
- Railway account (https://railway.app)
- GitHub account with repo access

### Step 1: Grant Railway Access to Repository

1. Go to GitHub Settings -> Applications -> Railway -> Configure
2. Add `synch-manager` repository to allowed repositories
3. Save changes

### Step 2: Create Railway Project

1. Go to https://railway.app/new
2. Click "GitHub Repository"
3. Search for `synch-manager`
4. Select the repository

### Step 3: Add PostgreSQL Database

1. In your Railway project, click "+ New"
2. Select "Database" -> "PostgreSQL"
3. Railway will auto-provision and inject DATABASE_URL

### Step 4: Configure Environment Variables

Add these environment variables in Railway:

```
DJANGO_SECRET_KEY=<generate-a-secure-key>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=<your-railway-domain>
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

### Step 5: Set Root Directory

In service settings, set Root Directory to `backend`

### Step 6: Deploy

Railway will automatically build and deploy from the `railway.json` config.

## Architecture

```
+------------------+     +------------------+     +------------------+
|   React Frontend |<--->|  Django Backend  |<--->|    MariaDB       |
|   (Port 5173)    |     |   (Port 8000)    |     |   (Port 3306)    |
+------------------+     +------------------+     +------------------+
                              |      |
                              v      v
                    +----------+  +------------+
                    |  Redis   |  | TimescaleDB|
                    | (6379)   |  |  (5432)    |
                    +----------+  +------------+
                              |
                              v
                    +------------------+
                    |  Kafka/Zookeeper |
                    |   (9092/2181)    |
                    +------------------+
```

## API Endpoints

| Module | Endpoint | Description |
|--------|----------|-------------|
| Inventory | `/api/v1/inventory/` | Network element registry |
| Fault | `/api/v1/fault/` | Alarms and trap management |
| Performance | `/api/v1/performance/` | MTIE/TDEV metrics |
| Security | `/api/v1/security/` | Users, roles, audit logs |
| PTP | `/api/v1/ptp/` | PTP client configuration |
| Configuration | `/api/v1/configuration/` | Config policies |
| War Mode | `/api/v1/war-mode/` | Tactical timing operations |
| NTG | `/api/v1/ntg/` | NTG device management |

## Development

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Documentation

- [Architecture](docs/architecture.md)
- [API Reference](docs/api-reference.md)
- [Deployment Guide](docs/deployment-guide.md)
- [Developer Setup](docs/developer-setup.md)

## License

MIT License - See LICENSE file for details.
