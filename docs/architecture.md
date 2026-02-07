# Synch-Manager Architecture

This document describes the architecture of the Synch-Manager platform, an open-source synchronization management system providing FCAPS management for PTP, NTP, and SyncE network elements.

The design is based on a five-tier architecture and uses only open-source components such as LinuxPTP, Chrony, Django, React, MariaDB, TimescaleDB, Kafka, Redis, and Grafana.

## 1. System Overview

Synch-Manager is a web-based, multi-tier synchronization management platform that provides centralized FCAPS functions for timing network elements (grandmasters, boundary clocks, SSUs, PTP clients, etc.).

Core objectives:

- Manage and monitor 100+ network elements and 10,000+ PTP clients (scalable higher).
- Provide real-time visibility of synchronization health and alarms.
- Use an entirely open-source stack, avoiding licensing and vendor lock-in.
- Expose all functionality via REST APIs for automation and integration.

## 2. Five-Tier Architecture

| Tier | Components and Responsibilities |
|-------------------|------------------------------------------------------------------------------------------------|
| Presentation | React SPA, Leaflet maps, charts, WebSocket-based real-time views |
| API Gateway | Django REST Framework, authentication, rate limiting, routing |
| Application Logic | Django apps for FCAPS (fault, config, inventory, performance, security, PTP) |
| Data Persistence | MariaDB (relational), TimescaleDB (time-series), Redis (cache, channels) |
| Device Communication | SNMP polling/traps, LinuxPTP management, NTP, SyncE, Kafka-based event streaming |

### 2.1 Component Diagram

```text
Browser (React SPA)
        |
  HTTPS / WebSocket
        |
  Nginx Reverse Proxy
        |
  Django + DRF + Channels
        |
+------------------------+----------------------------+
| MariaDB | TimescaleDB | Redis | Kafka | Prometheus |
+------------------------+----------------------------+
        |
  SNMP / SSH / PTP / NTP / SyncE
        |
  Network Elements (GM, BC, SSU, PTP clients)
```

## 3. Technology Stack

- Backend: Django 5.x, Django REST Framework, Channels.
- Frontend: React + TypeScript + Vite.
- Databases: MariaDB for relational data, TimescaleDB for time-series metrics.
- Messaging: Apache Kafka for events and northbound integration.
- Task Queue: Celery + Redis.
- SNMP: PySNMP for polling and trap processing.
- PTP/NTP: LinuxPTP (ptp4l, phc2sys) and Chrony.
- Visualization: Grafana for dashboards, Prometheus for metrics.
- Reverse Proxy: Nginx for HTTPS termination and static content.

## 4. FCAPS Modules

### 4.1 Fault Management

- SNMP trap receiver and normalizer.
- Alarm database with ITU-T X.733 fields (severity, probable cause, state).
- WebSocket push for real-time alarm viewer.
- Northbound SNMP trap, REST, and syslog forwarding.

### 4.2 Configuration Management

- Policy-based configuration (per NE type, card, port).
- SNMP SET / CLI / API-based application.
- Compliance auditing and policy violation alarms.
- Planned GitOps-style storage of policies as YAML in Git.

### 4.3 Inventory Management

- Auto-discovery via SNMP (sysDescr, sysObjectID, vendor-specific OIDs).
- NE registry with type, IP, location, and status.
- Detailed inventory of chassis, cards, modules, ports.
- Map-based visualization of NE locations.

### 4.4 Performance Management

- Periodic polling for MTIE, TDEV, phase, and frequency metrics.
- TimescaleDB hypertables and continuous aggregates (hourly, daily).
- Threshold crossing detection and SLA monitoring.
- Integration with MTIE mask library for standards checking.

### 4.5 Security Management

- Role-based access control (ADMIN, POWER, USER, VIEWER).
- Audit trail of all user actions.
- Password policy enforcement and account lockout.
- TLS for all external interfaces.

### 4.6 PTP Client Management

- Discovery of PTP clients and attributes.
- Monitoring of offset-from-master, path delay, and port states.
- Detection of sync loss and topology changes.
- Integration with LinuxPTP on Linux hosts.

## 5. Deployment Architecture

- Development: Single-node Docker Compose (backend, frontend, DBs, Kafka, Redis, Grafana).
- Production: Multi-node deployment with HA MariaDB (Galera), TimescaleDB replication, Kafka cluster, multiple Django instances behind Nginx.
- Monitoring: Prometheus exporters and Grafana dashboards for both system and application metrics.

## 6. Roadmap

Short-term priorities:

- Implement Fault, Inventory, and Configuration modules.
- Implement core PTP client management and performance collection.
- Provide initial Grafana dashboard for synchronization overview.

Longer-term enhancements:

- Machine learning anomaly detection for MTIE/TDEV data.
- GNSS spoofing/jamming detection.
- Multi-site hierarchical deployment and advanced topology views.
