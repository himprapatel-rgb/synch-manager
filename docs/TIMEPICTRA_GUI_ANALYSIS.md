# TimePictra GUI Analysis for Synch-Manager

## Overview

This document captures key learnings from the Microchip TimePictra EMS interface to guide GUI improvements for Synch-Manager.

---

## 1. Main Navigation Structure

TimePictra uses a **horizontal tab-based navigation** with the following primary sections:

| Tab | Purpose |
|-----|---------|
| **Dashboard** | Overview with widgets for alarms, inventory, charts |
| **Topology** | World map view showing device locations |
| **Fault** | Alarm viewer with filtering and acknowledgment |
| **Configuration** | Device configuration with logical panel diagrams |
| **Inventory** | Hardware inventory with serial numbers, firmware |
| **Performance** | Performance charts and metrics |
| **Security** | Security settings and policies |
| **PTP Client** | PTP-specific configuration |
| **System** | System administration (licenses, LDAP, etc.) |
| **Logs** | Transaction and activity logs |

### Recommendation for Synch-Manager
Add missing sections: **Topology Map**, **Logs/Audit Trail**, **System Administration**

---

## 2. Dashboard Layout

### TimePictra Dashboard Components

```
+------------------+------------------------+
| Network Devices  | Main Content Area      |
| (Tree View)      |                        |
| - Root           | +--------------------+ |
|   - ESB          | | Alarms Widget      | |
|   - Device1      | +--------------------+ |
|   - Device2      | | NE Inventory       | |
|                  | +--------------------+ |
| Legend           | | Alarm Chart        | |
| (Status Colors)  | +--------------------+ |
+------------------+------------------------+
```

### Key Dashboard Widgets

1. **Alarms Summary**
   - Last 7 Days count
   - Last 30 Days count
   - Total alarms

2. **NE Inventory Details**
   - Device type grouping
   - Count per type

3. **Alarm Severity Chart**
   - Bar chart showing Critical/Major/Minor/Other

4. **Logged-In User Details**
   - User ID, Login Time, Client Address

5. **License Information**
   - License types with counts (Total/Used/Available)

6. **Alarm Viewer Table**
   - Severity, ID, Source, Aid, Condition
   - Service Effect, NE Time, Description, Ack status

---

## 3. Device Management Features

### Right-Click Context Menu Options

| Action | Description |
|--------|-------------|
| Manage NE | Start managing the network element |
| UnManage NE | Stop managing the element |
| Delete NE | Remove from inventory |
| Alarms | View alarms for this device |
| Events | View events for this device |
| Forced Alarm Sync | Synchronize alarms |
| Force Unlock NE | Release locks |
| Configuration | Open configuration panel |
| Set Alarm Policy | Configure alarm policies |
| Performance Monitor | View performance data |
| NE User Admin | Manage device users |
| Inventory | View hardware inventory |
| NE Details | View detailed device info |
| Activity Log | View device activity |
| Pass Through | Direct device access |
| PTP Client | PTP configuration |
| IP Ping | Connectivity test |
| User Preferences | Device-specific preferences |
| Device User Guide | Documentation link |

### NE Details Dialog Fields

- Type (e.g., TimeProvider 4100)
- IP Address
- Comm Port (161 for SNMP)
- Protocol (IP)
- Manage Status (Y/N)
- Created By / Created On
- CLLI (Common Language Location Identifier)
- Location
- Enable/Disable Configuration Alignment
- Remarks
- NE Image (custom image support)

---

## 4. Configuration Module

### Logical Panel View

The configuration module displays a **visual diagram** showing:

- Physical card layout
- Service connections (GNSS, ETH, T1E1, PPS, TOD, NTP)
- Color-coded signal flows
- Connection status

### Services Displayed

| Service | Color | Description |
|---------|-------|-------------|
| Mgmt | Blue | Management interface |
| PTP | Green | Precision Time Protocol |
| SyncE | Purple | Synchronous Ethernet |
| NTP | Red | Network Time Protocol |
| GNSS | Black | GNSS receiver |
| TDM | Navy | TDM interfaces |

### View Modes
- **View Mode**: Read-only display
- **Modify Mode**: Edit configuration

---

## 5. Fault Management

### Alarm Viewer Features

1. **Filter Options**
   - Published Filters (saved filters)
   - Default view

2. **Action Buttons**
   - Sort, Filter
   - Hide/Show Ack Alarms
   - Discharge
   - Acknowledge All / UnAcknowledge All
   - Server Push (real-time updates)

3. **Alarm Table Columns**
   - Ack (checkbox)
   - Sev (severity icon)
   - ID
   - Source (device)
   - AID (Alarm ID)
   - Condition
   - Service Effecting
   - NE Time
   - Server Time
   - Description
   - Search Similar
   - Alarm Forward

4. **Alarm Summary**
   - Total Alarms count
   - Acknowledged count breakdown
   - Time Period filter

---

## 6. Inventory Management

### Inventory Table Columns

| Column | Description |
|--------|-------------|
| Sev | Severity indicator |
| Aid | Equipment ID |
| Source | Device identifier |
| Serial No | Hardware serial number |
| Model No | Part/Model number |
| CLEI | CLEI code |
| Firmware Rev | Firmware version |
| H/W Rev | Hardware revision |
| Equipment Type | Card/module type |
| Remarks | Notes/comments |

### Sub-tabs
- Filter
- Optional License
- NTP Peers
- PM Message
- LCT Log

---

## 7. Performance Monitoring

### Performance Selection Criteria

1. **Measurement Type**
   - Performance
   - Ethernet Status

2. **Date Criteria**
   - One-Day
   - One-Week
   - One-Month
   - Complete
   - Date Range (From/To)

3. **Performance Chart View**
   - Interactive charts
   - Element selection

---

## 8. Transaction Logs

### Log View Criteria

- Show All
- Last 7 days
- Last 30 days
- Date Range (From/To)

### Transaction Filters
- All Transactions
- CLLI
- Login/Logout
- Other Transactions

### Log Table Columns
- Time
- CLLI
- Transaction
- Aid
- Keyword
- New value
- Old value
- By User
- Object Type

---

## 9. Key UI/UX Patterns to Adopt

### 1. Color-Coded Status Legend

```
● Unmanaged (Gray)
● Managed (Green)
⊘ Unavailable (Red with line)
● Critical (Red)
● Major (Orange)
● Minor (Yellow)
● Manage Failed (Gray with X)
● Remanage (Gray refresh)
● Virtual (Gray outline)
● Others (Blue)
```

### 2. Hierarchical Tree Navigation
- Collapsible device tree on left sidebar
- Shows device status with colored icons
- Supports right-click context menus

### 3. Widget-Based Dashboard
- Multiple independent data widgets
- Refresh icons per widget
- Export/print capabilities

### 4. Data Tables
- Sortable columns
- Pagination
- Server-side filtering
- Report generation

### 5. Real-Time Updates
- Server Push functionality
- Auto-refresh indicators

---

## 10. Improvements for Synch-Manager

### Priority 1: Critical Missing Features

1. **World Map Topology View**
   - Show devices on interactive map
   - Status indicators on map pins

2. **Enhanced Alarm Management**
   - Acknowledge/UnAcknowledge
   - Alarm filtering by severity
   - Server Push for real-time updates

3. **Transaction/Activity Logs**
   - Audit trail for all actions
   - User activity tracking

4. **Configuration Visual Panel**
   - Logical diagram of device connections
   - Visual representation of signal flows

### Priority 2: Enhanced Features

5. **Right-Click Context Menus**
   - Device-specific actions
   - Quick access to common operations

6. **Advanced Filtering**
   - Saved filter presets
   - Complex filter combinations

7. **Report Generation**
   - Export to PDF/Excel
   - Scheduled reports

8. **License Management Dashboard**
   - Track license usage
   - Expiration warnings

### Priority 3: Polish

9. **Consistent Status Colors**
   - Standardize color scheme
   - Add legend component

10. **Performance Charts**
    - Date range selection
    - Multiple metric comparison

---

## 11. Data Model Additions

Based on TimePictra, consider adding these fields to Synch-Manager models:

### NetworkElement Model
```python
# Additional fields to consider
clli = models.CharField(max_length=100)  # Common Language Location ID
comm_port = models.IntegerField(default=161)  # SNMP port
protocol = models.CharField(max_length=20)  # IP, etc.
created_by = models.ForeignKey(User)
config_alignment_enabled = models.BooleanField(default=True)
remarks = models.TextField(blank=True)
ne_image = models.ImageField(null=True)  # Custom device image
```

### TransactionLog Model (New)
```python
class TransactionLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    clli = models.CharField(max_length=100)
    transaction_type = models.CharField(max_length=50)
    aid = models.CharField(max_length=100)
    keyword = models.CharField(max_length=100)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    user = models.ForeignKey(User)
    object_type = models.CharField(max_length=50)
```

### License Model (New)
```python
class License(models.Model):
    license_type = models.CharField(max_length=50)
    total_count = models.IntegerField()
    used_count = models.IntegerField()
    expiry_date = models.DateField(null=True)
```

---

## 12. API Endpoints to Add

```
GET  /api/v1/topology/map-data/
GET  /api/v1/logs/transactions/
POST /api/v1/alarms/{id}/acknowledge/
POST /api/v1/alarms/bulk-acknowledge/
GET  /api/v1/licenses/
GET  /api/v1/inventory/{ne_id}/hardware/
POST /api/v1/network-elements/{id}/ping/
GET  /api/v1/performance/charts/
```

---

## Summary

TimePictra provides a comprehensive EMS interface with:
- Rich dashboard with multiple data widgets
- Hierarchical device navigation
- Visual configuration panels
- Extensive alarm management
- Detailed audit logging

Synch-Manager should prioritize adding:
1. Topology map view
2. Enhanced alarm acknowledgment
3. Transaction logging
4. Visual configuration panels
5. Right-click context menus

These improvements will bring Synch-Manager closer to enterprise-grade functionality.
