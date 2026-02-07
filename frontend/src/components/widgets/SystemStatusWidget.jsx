import React, { useState, useEffect } from 'react';
import '../../styles/SystemStatusWidget.css';

const SystemStatusWidget = () => {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [systemHealth, setSystemHealth] = useState({
    overall: 'healthy',
    score: 95
  });

  useEffect(() => {
    // Mock data - replace with API call
    const mockDevices = [
      {
        id: 1,
        name: 'TP4100-Main',
        type: 'TimeProvider 4100',
        status: 'online',
        health: 98,
        syncStatus: 'Locked',
        lastUpdate: new Date(Date.now() - 2 * 60 * 1000).toISOString()
      },
      {
        id: 2,
        name: 'TP4100-Backup',
        status: 'online',
        type: 'TimeProvider 4100',
        health: 95,
        syncStatus: 'Locked',
        lastUpdate: new Date(Date.now() - 3 * 60 * 1000).toISOString()
      },
      {
        id: 3,
        name: 'SyncServer-01',
        type: 'Sync Server S650',
        status: 'warning',
        health: 75,
        syncStatus: 'Degraded',
        lastUpdate: new Date(Date.now() - 10 * 60 * 1000).toISOString()
      },
      {
        id: 4,
        name: 'GPS-Module-1',
        type: 'GPS Antenna',
        status: 'online',
        health: 100,
        syncStatus: 'Locked',
        lastUpdate: new Date(Date.now() - 1 * 60 * 1000).toISOString()
      },
      {
        id: 5,
        name: 'NTP-Server-01',
        type: 'NTP Server',
        status: 'offline',
        health: 0,
        syncStatus: 'No Signal',
        lastUpdate: new Date(Date.now() - 60 * 60 * 1000).toISOString()
      }
    ];

    setTimeout(() => {
      setDevices(mockDevices);
      setLoading(false);
    }, 500);
  }, []);

  const getStatusClass = (status) => {
    switch (status) {
      case 'online': return 'status-online';
      case 'offline': return 'status-offline';
      case 'warning': return 'status-warning';
      case 'error': return 'status-error';
      default: return '';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'online': return '🟢';
      case 'offline': return '🔴';
      case 'warning': return '🟡';
      case 'error': return '🔴';
      default: return '⚪';
    }
  };

  const getSyncStatusClass = (syncStatus) => {
    switch (syncStatus) {
      case 'Locked': return 'sync-locked';
      case 'Degraded': return 'sync-degraded';
      case 'No Signal': return 'sync-no-signal';
      default: return '';
    }
  };

  const formatLastUpdate = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 60) {
      return `${diffMins}m ago`;
    } else {
      return `${Math.floor(diffMins / 60)}h ago`;
    }
  };

  const getHealthBarColor = (health) => {
    if (health >= 90) return '#4caf50';
    if (health >= 70) return '#ff9800';
    return '#f44336';
  };

  if (loading) {
    return (
      <div className="system-status-widget loading">
        <div className="loading-spinner">Loading system status...</div>
      </div>
    );
  }

  const onlineCount = devices.filter(d => d.status === 'online').length;
  const totalCount = devices.length;

  return (
    <div className="system-status-widget">
      <div className="widget-header">
        <h3>System Status</h3>
        <div className="health-indicator">
          <span className="health-label">System Health:</span>
          <span className={`health-value health-${systemHealth.overall}`}>
            {systemHealth.score}%
          </span>
        </div>
      </div>

      <div className="status-summary">
        <div className="summary-item">
          <span className="summary-icon">🟢</span>
          <div className="summary-content">
            <div className="summary-value">{onlineCount}</div>
            <div className="summary-label">Online</div>
          </div>
        </div>
        <div className="summary-item">
          <span className="summary-icon">💻</span>
          <div className="summary-content">
            <div className="summary-value">{totalCount}</div>
            <div className="summary-label">Total Devices</div>
          </div>
        </div>
        <div className="summary-item">
          <span className="summary-icon">🔒</span>
          <div className="summary-content">
            <div className="summary-value">{devices.filter(d => d.syncStatus === 'Locked').length}</div>
            <div className="summary-label">Sync Locked</div>
          </div>
        </div>
      </div>

      <div className="devices-list">
        <h4>Devices</h4>
        {devices.map((device) => (
          <div key={device.id} className={`device-item ${getStatusClass(device.status)}`}>
            <div className="device-status-icon">
              {getStatusIcon(device.status)}
            </div>
            <div className="device-info">
              <div className="device-name">{device.name}</div>
              <div className="device-type">{device.type}</div>
            </div>
            <div className="device-metrics">
              <div className="metric">
                <span className="metric-label">Health:</span>
                <div className="health-bar">
                  <div 
                    className="health-fill"
                    style={{ 
                      width: `${device.health}%`,
                      backgroundColor: getHealthBarColor(device.health)
                    }}
                  />
                </div>
                <span className="metric-value">{device.health}%</span>
              </div>
              <div className="metric">
                <span className="metric-label">Sync:</span>
                <span className={`sync-badge ${getSyncStatusClass(device.syncStatus)}`}>
                  {device.syncStatus}
                </span>
              </div>
            </div>
            <div className="device-update">
              <span className="update-label">Last update:</span>
              <span className="update-time">{formatLastUpdate(device.lastUpdate)}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="widget-footer">
        <button className="btn-manage" onClick={() => window.location.href = '/inventory'}>
          Manage Devices
        </button>
        <button className="btn-refresh" onClick={() => window.location.reload()}>
          🔄 Refresh
        </button>
      </div>
    </div>
  );
};

export default SystemStatusWidget;
