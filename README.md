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

## Quick Start

```bash
cp .env.example .env
docker-compose up -d
docker-compose run --rm web python manage.py migrate
docker-compose run --rm web python manage.py createsuperuser
```

Endpoints:

- Backend API health: `http://localhost:8000/api/v1/health/`
- Grafana: `http://localhost:3000`
- React (dev): `http://localhost:5173`

## Documentation

- [Architecture](docs/architecture.md)
- [API Reference](docs/api-reference.md)
- [Deployment Guide](docs/deployment-guide.md)
- [Developer Setup](docs/developer-setup.md)

## License

Apache 2.0
