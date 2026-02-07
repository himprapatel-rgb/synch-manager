import React, { useState, useEffect } from 'react';
import '../../styles/PerformanceWidget.css';

const PerformanceWidget = () => {
  const [performanceData, setPerformanceData] = useState({
    cpuUsage: 0,
    memoryUsage: 0,
    diskUsage: 0,
    networkThroughput: 0,
    uptime: 0
  });
  const [loading, setLoading] = useState(true);
  const [history, setHistory] = useState({
    cpu: [],
    memory: [],
    network: []
  });

  useEffect(() => {
    // Mock data - replace with API call
    const mockData = {
      cpuUsage: Math.floor(Math.random() * 40) + 20,
      memoryUsage: Math.floor(Math.random() * 30) + 40,
      diskUsage: Math.floor(Math.random() * 20) + 60,
      networkThroughput: Math.floor(Math.random() * 500) + 200,
      uptime: 1234567 // seconds
    };

    const mockHistory = {
      cpu: Array.from({ length: 20 }, () => Math.floor(Math.random() * 40) + 20),
      memory: Array.from({ length: 20 }, () => Math.floor(Math.random() * 30) + 40),
      network: Array.from({ length: 20 }, () => Math.floor(Math.random() * 500) + 200)
    };

    setTimeout(() => {
      setPerformanceData(mockData);
      setHistory(mockHistory);
      setLoading(false);
    }, 500);

    // Simulate real-time updates
    const interval = setInterval(() => {
      setPerformanceData(prev => ({
        ...prev,
        cpuUsage: Math.min(100, Math.max(0, prev.cpuUsage + (Math.random() * 10 - 5))),
        memoryUsage: Math.min(100, Math.max(0, prev.memoryUsage + (Math.random() * 5 - 2.5))),
        networkThroughput: Math.max(0, prev.networkThroughput + (Math.random() * 100 - 50)),
        uptime: prev.uptime + 5
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const getUsageClass = (value) => {
    if (value >= 80) return 'usage-critical';
    if (value >= 60) return 'usage-warning';
    return 'usage-normal';
  };

  const formatUptime = (seconds) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${days}d ${hours}h ${minutes}m`;
  };

  const formatThroughput = (mbps) => {
    if (mbps >= 1000) {
      return `${(mbps / 1000).toFixed(2)} Gbps`;
    }
    return `${mbps.toFixed(0)} Mbps`;
  };

  if (loading) {
    return (
      <div className="performance-widget loading">
        <div className="loading-spinner">Loading performance data...</div>
      </div>
    );
  }

  return (
    <div className="performance-widget">
      <div className="widget-header">
        <h3>System Performance</h3>
        <button className="btn-details" onClick={() => window.location.href = '/performance'}>
          View Details
        </button>
      </div>

      <div className="performance-metrics">
        <div className="metric-item">
          <div className="metric-header">
            <span className="metric-label">CPU Usage</span>
            <span className={`metric-value ${getUsageClass(performanceData.cpuUsage)}`}>
              {performanceData.cpuUsage.toFixed(1)}%
            </span>
          </div>
          <div className="progress-bar">
            <div 
              className={`progress-fill ${getUsageClass(performanceData.cpuUsage)}`}
              style={{ width: `${performanceData.cpuUsage}%` }}
            />
          </div>
          <div className="metric-chart">
            {history.cpu.map((val, idx) => (
              <div 
                key={idx} 
                className="chart-bar"
                style={{ height: `${val}%` }}
                title={`${val.toFixed(1)}%`}
              />
            ))}
          </div>
        </div>

        <div className="metric-item">
          <div className="metric-header">
            <span className="metric-label">Memory Usage</span>
            <span className={`metric-value ${getUsageClass(performanceData.memoryUsage)}`}>
              {performanceData.memoryUsage.toFixed(1)}%
            </span>
          </div>
          <div className="progress-bar">
            <div 
              className={`progress-fill ${getUsageClass(performanceData.memoryUsage)}`}
              style={{ width: `${performanceData.memoryUsage}%` }}
            />
          </div>
          <div className="metric-chart">
            {history.memory.map((val, idx) => (
              <div 
                key={idx} 
                className="chart-bar"
                style={{ height: `${val}%` }}
                title={`${val.toFixed(1)}%`}
              />
            ))}
          </div>
        </div>

        <div className="metric-item">
          <div className="metric-header">
            <span className="metric-label">Disk Usage</span>
            <span className={`metric-value ${getUsageClass(performanceData.diskUsage)}`}>
              {performanceData.diskUsage.toFixed(1)}%
            </span>
          </div>
          <div className="progress-bar">
            <div 
              className={`progress-fill ${getUsageClass(performanceData.diskUsage)}`}
              style={{ width: `${performanceData.diskUsage}%` }}
            />
          </div>
          <div className="metric-info">
            <span>Used: 120 GB / Total: 200 GB</span>
          </div>
        </div>

        <div className="metric-item">
          <div className="metric-header">
            <span className="metric-label">Network Throughput</span>
            <span className="metric-value">
              {formatThroughput(performanceData.networkThroughput)}
            </span>
          </div>
          <div className="metric-chart network-chart">
            {history.network.map((val, idx) => (
              <div 
                key={idx} 
                className="chart-bar"
                style={{ height: `${(val / 1000) * 100}%` }}
                title={`${formatThroughput(val)}`}
              />
            ))}
          </div>
        </div>
      </div>

      <div className="system-info">
        <div className="info-item">
          <span className="info-icon">⏱️</span>
          <div className="info-content">
            <div className="info-label">System Uptime</div>
            <div className="info-value">{formatUptime(performanceData.uptime)}</div>
          </div>
        </div>
        <div className="info-item">
          <span className="info-icon">📊</span>
          <div className="info-content">
            <div className="info-label">Active Processes</div>
            <div className="info-value">127</div>
          </div>
        </div>
        <div className="info-item">
          <span className="info-icon">🔌</span>
          <div className="info-content">
            <div className="info-label">Network Connections</div>
            <div className="info-value">34</div>
          </div>
        </div>
      </div>

      <div className="widget-footer">
        <button className="btn-refresh" onClick={() => window.location.reload()}>
          🔄 Refresh
        </button>
        <span className="update-time">Last updated: {new Date().toLocaleTimeString()}</span>
      </div>
    </div>
  );
};

export default PerformanceWidget;
