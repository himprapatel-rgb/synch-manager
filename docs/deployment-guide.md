# Synch-Manager Deployment Guide

This guide describes how to deploy Synch-Manager using Docker Compose for development and as a baseline for production.

## 1. Prerequisites

- Linux host (e.g. Ubuntu 22.04 or Rocky Linux 9).
- Docker Engine and Docker Compose installed.
- At least 16 GB RAM, 4 vCPUs, 200 GB disk.
- Network reachability to managed devices over SNMP, PTP, NTP.

## 2. Quick Start (Development)

1. Clone repository:

```bash
git clone https://github.com/himprapatel-rgb/synch-manager.git
cd synch-manager
```

2. Create environment file:

```bash
cp .env.example .env
# Edit values as needed (DB passwords, secrets, hostnames)
```

3. Start services:

```bash
docker-compose up -d
```

4. Initialize Django:

```bash
docker-compose run --rm web python manage.py migrate
docker-compose run --rm web python manage.py createsuperuser
```

5. Verify health:

- Backend API: `http://localhost:8000/api/v1/health/`
- Grafana: `http://localhost:3000`

## 3. Services

The `docker-compose.yml` file starts:

- `web`: Django backend.
- `celery`, `celery-beat`: background tasks and schedulers.
- `snmp-trap-receiver`: SNMP trap listening service.
- `mariadb`: relational database.
- `timescaledb`: time-series database.
- `redis`: cache and Celery broker.
- `zookeeper`, `kafka`: event streaming.
- `grafana`: dashboards.
- `frontend`: React dev server.

## 4. Production Considerations

For production, recommended changes:

- Use `docker-compose.prod.yml` (to be defined) with:
  - Multiple `web` containers behind Nginx.
  - Externalized MariaDB Galera cluster.
  - Managed PostgreSQL/Timescale cluster.
  - Kafka cluster with 3 brokers.
- Configure HTTPS in `nginx/nginx.conf`.
- Use strong secrets and non-default passwords.
- Enable backups for MariaDB and TimescaleDB.

## 5. Backup and Restore

Backups are handled by `scripts/backup_databases.sh` (to be implemented):

- Dumps MariaDB database with `mysqldump`.
- Dumps TimescaleDB database with `pg_dump`.
- Compresses output and rotates old backups.

To restore:

- Pipe SQL dumps back into the running DB containers.
- Restart dependent services if required.

## 6. Monitoring

- Prometheus scrapes Django and Celery metrics via django-prometheus and custom exporters.
- Grafana dashboards visualize:
  - Application health.
  - Alarm rates.
  - NE count and status.
  - Performance metric volumes.

This baseline deployment can be adapted to Kubernetes or other orchestrators in future phases.
