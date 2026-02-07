import React, { useState, useEffect } from 'react';
import '../../styles/AlarmSummaryWidget.css';

const AlarmSummaryWidget = () => {
  const [alarms, setAlarms] = useState({
    critical: 0,
    major: 0,
    minor: 0,
    warning: 0,
    total: 0
  });
  const [recentAlarms, setRecentAlarms] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Mock data - replace with API call
    const mockAlarmCounts = {
      critical: 2,
      major: 5,
      minor: 12,
      warning: 8,
      total: 27
    };

    const mockRecentAlarms = [
      {
        id: 1,
        severity: 'critical',
        device: 'TP4100-Main',
        message: 'GPS signal lost',
        timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString()
      },
      {
        id: 2,
        severity: 'major',
        device: 'SyncServer-01',
        message: 'NTP synchronization degraded',
        timestamp: new Date(Date.now() - 15 * 60 * 1000).toISOString()
      },
      {
        id: 3,
        severity: 'critical',
        device: 'TP4100-Backup',
        message: 'System temperature exceeded threshold',
        timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString()
      },
      {
        id: 4,
        severity: 'minor',
        device: 'GPS-Module-1',
        message: 'Low satellite count',
        timestamp: new Date(Date.now() - 45 * 60 * 1000).toISOString()
      },
      {
        id: 5,
        severity: 'warning',
        device: 'TP4100-Main',
        message: 'Configuration backup recommended',
        timestamp: new Date(Date.now() - 60 * 60 * 1000).toISOString()
      }
    ];

    setTimeout(() => {
      setAlarms(mockAlarmCounts);
      setRecentAlarms(mockRecentAlarms);
      setLoading(false);
    }, 500);
  }, []);

  const getSeverityClass = (severity) => {
    switch (severity) {
      case 'critical': return 'severity-critical';
      case 'major': return 'severity-major';
      case 'minor': return 'severity-minor';
      case 'warning': return 'severity-warning';
      default: return '';
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical': return '⚠️';
      case 'major': return '🔴';
      case 'minor': return '🟡';
      case 'warning': return '⚠️';
      default: return '❔';
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 60) {
      return `${diffMins} min ago`;
    } else if (diffMins < 1440) {
      return `${Math.floor(diffMins / 60)} hr ago`;
    } else {
      return date.toLocaleString();
    }
  };

  if (loading) {
    return (
      <div className="alarm-summary-widget loading">
        <div className="loading-spinner">Loading alarms...</div>
      </div>
    );
  }

  return (
    <div className="alarm-summary-widget">
      <div className="widget-header">
        <h3>Alarm Summary</h3>
        <button className="btn-view-all" onClick={() => window.location.href = '/alarms'}>
          View All
        </button>
      </div>

      <div className="alarm-counts">
        <div className="alarm-count-item critical">
          <div className="count-icon">⚠️</div>
          <div className="count-details">
            <div className="count-value">{alarms.critical}</div>
            <div className="count-label">Critical</div>
          </div>
        </div>
        <div className="alarm-count-item major">
          <div className="count-icon">🔴</div>
          <div className="count-details">
            <div className="count-value">{alarms.major}</div>
            <div className="count-label">Major</div>
          </div>
        </div>
        <div className="alarm-count-item minor">
          <div className="count-icon">🟡</div>
          <div className="count-details">
            <div className="count-value">{alarms.minor}</div>
            <div className="count-label">Minor</div>
          </div>
        </div>
        <div className="alarm-count-item warning">
          <div className="count-icon">⚠️</div>
          <div className="count-details">
            <div className="count-value">{alarms.warning}</div>
            <div className="count-label">Warning</div>
          </div>
        </div>
      </div>

      <div className="total-alarms">
        <span className="total-label">Total Active Alarms:</span>
        <span className="total-value">{alarms.total}</span>
      </div>

      <div className="recent-alarms">
        <h4>Recent Alarms</h4>
        <div className="alarms-list">
          {recentAlarms.map((alarm) => (
            <div key={alarm.id} className={`alarm-item ${getSeverityClass(alarm.severity)}`}>
              <div className="alarm-severity-icon">
                {getSeverityIcon(alarm.severity)}
              </div>
              <div className="alarm-content">
                <div className="alarm-device">{alarm.device}</div>
                <div className="alarm-message">{alarm.message}</div>
                <div className="alarm-timestamp">{formatTimestamp(alarm.timestamp)}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="widget-footer">
        <button className="btn-acknowledge" onClick={() => alert('Acknowledge all alarms')}>
          Acknowledge All
        </button>
        <button className="btn-refresh" onClick={() => window.location.reload()}>
          🔄 Refresh
        </button>
      </div>
    </div>
  );
};

export default AlarmSummaryWidget;
