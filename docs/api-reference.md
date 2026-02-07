# Synch-Manager API Reference

This document defines the main REST API endpoints for external integrations and the React frontend. All endpoints are versioned under `/api/v1/`.

## 1. Authentication

### 1.1 Obtain JWT Token

- Method: `POST`
- Path: `/api/v1/auth/token/`
- Body (JSON):

```json
{
  "username": "admin",
  "password": "secret"
}
```

- Response:

```json
{
  "access": "<access_token>",
  "refresh": "<refresh_token>"
}
```

### 1.2 Refresh Token

- Method: `POST`
- Path: `/api/v1/auth/token/refresh/`

```json
{
  "refresh": "<refresh_token>"
}
```

## 2. Health

### 2.1 Service Health Check

- Method: `GET`
- Path: `/api/v1/health/`
- Auth: Not required

Response example:

```json
{
  "status": "ok",
  "service": "synch-manager"
}
```

## 3. Fault Management

### 3.1 List Active Alarms

- Method: `GET`
- Path: `/api/v1/fault/alarms/active/`
- Query:
  - `severity` (optional): CRITICAL, MAJOR, MINOR, WARNING, CLEAR
  - `ne` (optional): NE ID

Example response:

```json
[
  {
    "id": 101,
    "ne_id": 1,
    "ne_name": "TP5000-SITE-01",
    "alarm_type": "GNSS_SIGNAL_LOSS",
    "severity": "CRITICAL",
    "description": "GNSS signal lost",
    "raised_time": "2026-02-07T00:00:00Z",
    "state": "ACTIVE"
  }
]
```

### 3.2 Acknowledge Alarm

- Method: `POST`
- Path: `/api/v1/fault/alarms/{id}/ack/`

Body (optional):

```json
{
  "comment": "Investigating"
}
```

## 4. Inventory Management

### 4.1 List Network Elements

- Method: `GET`
- Path: `/api/v1/inventory/network-elements/`
- Query:
  - `type` (optional): NE type filter
  - `state` (optional): MANAGED, UNMANAGED, UNAVAILABLE

### 4.2 Create Network Element

- Method: `POST`
- Path: `/api/v1/inventory/network-elements/`

```json
{
  "name": "TP5000-SITE-01",
  "ne_type": "TimeProvider5000",
  "ip_address": "192.168.10.50",
  "snmp_community": "public",
  "management_state": "MANAGED"
}
```

### 4.3 Trigger Discovery

- Method: `POST`
- Path: `/api/v1/inventory/network-elements/{id}/discover/`

## 5. Configuration Management

### 5.1 List Policy Groups

- Method: `GET`
- Path: `/api/v1/config/policy-groups/`

### 5.2 Apply Policy Group to NE

- Method: `POST`
- Path: `/api/v1/config/policy-groups/{id}/apply/`

Body:

```json
{
  "ne_id": 1
}
```

## 6. Performance Management

### 6.1 Get Performance Series

- Method: `GET`
- Path: `/api/v1/performance/series/`

Query:

- `ne_id` (required)
- `metric_type` (MTIE, TDEV, PHASE, FREQUENCY)
- `start_time`, `end_time`
- `aggregation` (raw, hourly, daily)

Response (simplified):

```json
{
  "x": ["2026-02-07T00:00:00Z", "2026-02-07T00:01:00Z"],
  "y": [10.5, 11.2],
  "metric_type": "MTIE"
}
```

## 7. PTP Client Management

### 7.1 List PTP Clients

- Method: `GET`
- Path: `/api/v1/ptp/clients/`

### 7.2 Get Client Metrics

- Method: `GET`
- Path: `/api/v1/ptp/clients/{id}/metrics/`

## 8. Security and Audit

### 8.1 User Activity Log

- Method: `GET`
- Path: `/api/v1/security/audit-log/`
- Query filters: `user`, `action`, `from`, `to`

This API reference will evolve alongside the implementation. Each module folder (`apps/fault`, `apps/inventory`, etc.) will contain its own detailed serializers and viewsets aligned with these endpoints.
