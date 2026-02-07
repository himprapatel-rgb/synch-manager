import React, { useState, useEffect } from 'react';
import '../styles/Logs.css';

const Logs = () => {
  const [logs, setLogs] = useState([]);
  const [filteredLogs, setFilteredLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    dateFrom: '',
    dateTo: '',
    transactionType: 'all',
    user: '',
    device: '',
    status: 'all'
  });
  const [sortConfig, setSortConfig] = useState({
    key: 'timestamp',
    direction: 'desc'
  });
  const [currentPage, setCurrentPage] = useState(1);
  const logsPerPage = 50;

  // Mock data - replace with API call
  useEffect(() => {
    const mockLogs = Array.from({ length: 150 }, (_, i) => ({
      id: i + 1,
      timestamp: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
      transactionType: ['Configuration', 'Firmware Upgrade', 'Alarm Acknowledge', 'User Login', 'Device Restart', 'Parameter Change'][Math.floor(Math.random() * 6)],
      user: ['admin', 'operator1', 'engineer2', 'system'][Math.floor(Math.random() * 4)],
      device: ['TP4100-Main', 'TP4100-Backup', 'SyncServer-01', 'GPS-Module-1'][Math.floor(Math.random() * 4)],
      status: ['Success', 'Failed', 'Warning'][Math.floor(Math.random() * 3)],
      description: [
        'Configuration updated successfully',
        'Firmware upgrade completed',
        'Alarm acknowledged by user',
        'User logged in from 192.168.3.100',
        'Device restarted remotely',
        'NTP server parameter changed',
        'GPS synchronization restored',
        'Failed to connect to device'
      ][Math.floor(Math.random() * 8)],
      ipAddress: `192.168.3.${Math.floor(Math.random() * 255)}`
    }));
    
    setTimeout(() => {
      setLogs(mockLogs);
      setFilteredLogs(mockLogs);
      setLoading(false);
    }, 500);
  }, []);

  // Apply filters
  useEffect(() => {
    let result = [...logs];

    if (filters.dateFrom) {
      result = result.filter(log => new Date(log.timestamp) >= new Date(filters.dateFrom));
    }
    if (filters.dateTo) {
      result = result.filter(log => new Date(log.timestamp) <= new Date(filters.dateTo));
    }
    if (filters.transactionType !== 'all') {
      result = result.filter(log => log.transactionType === filters.transactionType);
    }
    if (filters.user) {
      result = result.filter(log => log.user.toLowerCase().includes(filters.user.toLowerCase()));
    }
    if (filters.device) {
      result = result.filter(log => log.device.toLowerCase().includes(filters.device.toLowerCase()));
    }
    if (filters.status !== 'all') {
      result = result.filter(log => log.status === filters.status);
    }

    setFilteredLogs(result);
    setCurrentPage(1);
  }, [filters, logs]);

  // Sort logs
  const handleSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });

    const sorted = [...filteredLogs].sort((a, b) => {
      if (a[key] < b[key]) return direction === 'asc' ? -1 : 1;
      if (a[key] > b[key]) return direction === 'asc' ? 1 : -1;
      return 0;
    });

    setFilteredLogs(sorted);
  };

  // Handle filter changes
  const handleFilterChange = (key, value) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  // Clear all filters
  const clearFilters = () => {
    setFilters({
      dateFrom: '',
      dateTo: '',
      transactionType: 'all',
      user: '',
      device: '',
      status: 'all'
    });
  };

  // Export logs
  const exportLogs = (format) => {
    if (format === 'csv') {
      const headers = ['Timestamp', 'Transaction Type', 'User', 'Device', 'Status', 'IP Address', 'Description'];
      const csvContent = [
        headers.join(','),
        ...filteredLogs.map(log => [
          log.timestamp,
          log.transactionType,
          log.user,
          log.device,
          log.status,
          log.ipAddress,
          `"${log.description}"`
        ].join(','))
      ].join('\n');

      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `transaction_logs_${new Date().toISOString().split('T')[0]}.csv`;
      a.click();
    }
  };

  // Pagination
  const indexOfLastLog = currentPage * logsPerPage;
  const indexOfFirstLog = indexOfLastLog - logsPerPage;
  const currentLogs = filteredLogs.slice(indexOfFirstLog, indexOfLastLog);
  const totalPages = Math.ceil(filteredLogs.length / logsPerPage);

  const getStatusClass = (status) => {
    switch (status) {
      case 'Success': return 'status-success';
      case 'Failed': return 'status-failed';
      case 'Warning': return 'status-warning';
      default: return '';
    }
  };

  return (
    <div className="logs-container">
      <div className="logs-header">
        <h1>Transaction Logs</h1>
        <div className="header-actions">
          <button className="btn-export" onClick={() => exportLogs('csv')}>
            <span className="icon">📥</span> Export CSV
          </button>
          <button className="btn-refresh" onClick={() => window.location.reload()}>
            <span className="icon">🔄</span> Refresh
          </button>
        </div>
      </div>

      <div className="filter-panel">
        <div className="filter-row">
          <div className="filter-group">
            <label>From Date:</label>
            <input
              type="datetime-local"
              value={filters.dateFrom}
              onChange={(e) => handleFilterChange('dateFrom', e.target.value)}
            />
          </div>
          <div className="filter-group">
            <label>To Date:</label>
            <input
              type="datetime-local"
              value={filters.dateTo}
              onChange={(e) => handleFilterChange('dateTo', e.target.value)}
            />
          </div>
          <div className="filter-group">
            <label>Transaction Type:</label>
            <select
              value={filters.transactionType}
              onChange={(e) => handleFilterChange('transactionType', e.target.value)}
            >
              <option value="all">All Types</option>
              <option value="Configuration">Configuration</option>
              <option value="Firmware Upgrade">Firmware Upgrade</option>
              <option value="Alarm Acknowledge">Alarm Acknowledge</option>
              <option value="User Login">User Login</option>
              <option value="Device Restart">Device Restart</option>
              <option value="Parameter Change">Parameter Change</option>
            </select>
          </div>
          <div className="filter-group">
            <label>User:</label>
            <input
              type="text"
              placeholder="Filter by user..."
              value={filters.user}
              onChange={(e) => handleFilterChange('user', e.target.value)}
            />
          </div>
          <div className="filter-group">
            <label>Device:</label>
            <input
              type="text"
              placeholder="Filter by device..."
              value={filters.device}
              onChange={(e) => handleFilterChange('device', e.target.value)}
            />
          </div>
          <div className="filter-group">
            <label>Status:</label>
            <select
              value={filters.status}
              onChange={(e) => handleFilterChange('status', e.target.value)}
            >
              <option value="all">All Status</option>
              <option value="Success">Success</option>
              <option value="Failed">Failed</option>
              <option value="Warning">Warning</option>
            </select>
          </div>
          <button className="btn-clear-filters" onClick={clearFilters}>
            Clear Filters
          </button>
        </div>
      </div>

      <div className="logs-stats">
        <div className="stat-item">
          <span className="stat-label">Total Logs:</span>
          <span className="stat-value">{logs.length}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Filtered:</span>
          <span className="stat-value">{filteredLogs.length}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Success:</span>
          <span className="stat-value success">{filteredLogs.filter(l => l.status === 'Success').length}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Failed:</span>
          <span className="stat-value failed">{filteredLogs.filter(l => l.status === 'Failed').length}</span>
        </div>
      </div>

      {loading ? (
        <div className="loading-spinner">Loading logs...</div>
      ) : (
        <>
          <div className="logs-table-wrapper">
            <table className="logs-table">
              <thead>
                <tr>
                  <th onClick={() => handleSort('id')}>
                    ID {sortConfig.key === 'id' && (sortConfig.direction === 'asc' ? '▲' : '▼')}
                  </th>
                  <th onClick={() => handleSort('timestamp')}>
                    Timestamp {sortConfig.key === 'timestamp' && (sortConfig.direction === 'asc' ? '▲' : '▼')}
                  </th>
                  <th onClick={() => handleSort('transactionType')}>
                    Transaction Type {sortConfig.key === 'transactionType' && (sortConfig.direction === 'asc' ? '▲' : '▼')}
                  </th>
                  <th onClick={() => handleSort('user')}>
                    User {sortConfig.key === 'user' && (sortConfig.direction === 'asc' ? '▲' : '▼')}
                  </th>
                  <th onClick={() => handleSort('device')}>
                    Device {sortConfig.key === 'device' && (sortConfig.direction === 'asc' ? '▲' : '▼')}
                  </th>
                  <th onClick={() => handleSort('status')}>
                    Status {sortConfig.key === 'status' && (sortConfig.direction === 'asc' ? '▲' : '▼')}
                  </th>
                  <th>IP Address</th>
                  <th>Description</th>
                </tr>
              </thead>
              <tbody>
                {currentLogs.map((log) => (
                  <tr key={log.id}>
                    <td>{log.id}</td>
                    <td>{new Date(log.timestamp).toLocaleString()}</td>
                    <td><span className="transaction-type">{log.transactionType}</span></td>
                    <td>{log.user}</td>
                    <td>{log.device}</td>
                    <td>
                      <span className={`status-badge ${getStatusClass(log.status)}`}>
                        {log.status}
                      </span>
                    </td>
                    <td>{log.ipAddress}</td>
                    <td className="description">{log.description}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="pagination">
            <div className="pagination-info">
              Showing {indexOfFirstLog + 1} to {Math.min(indexOfLastLog, filteredLogs.length)} of {filteredLogs.length} logs
            </div>
            <div className="pagination-controls">
              <button
                onClick={() => setCurrentPage(1)}
                disabled={currentPage === 1}
                className="btn-page"
              >
                First
              </button>
              <button
                onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                disabled={currentPage === 1}
                className="btn-page"
              >
                Previous
              </button>
              <span className="page-indicator">
                Page {currentPage} of {totalPages}
              </span>
              <button
                onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                disabled={currentPage === totalPages}
                className="btn-page"
              >
                Next
              </button>
              <button
                onClick={() => setCurrentPage(totalPages)}
                disabled={currentPage === totalPages}
                className="btn-page"
              >
                Last
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Logs;
