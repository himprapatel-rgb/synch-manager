import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AlertTriangle, Bell, BellOff, CheckCircle, Filter, RefreshCw, Search, Volume2, XCircle } from 'lucide-react';
import './AlarmManagement.css';

const SEVERITY_CONFIG = {
  critical: { color: 'bg-red-600', icon: XCircle, priority: 1 },
  major: { color: 'bg-orange-500', icon: AlertTriangle, priority: 2 },
  minor: { color: 'bg-yellow-500', icon: AlertTriangle, priority: 3 },
  warning: { color: 'bg-blue-500', icon: Bell, priority: 4 },
  info: { color: 'bg-gray-500', icon: Bell, priority: 5 }
};

const AlarmManagement = () => {
  const [alarms, setAlarms] = useState([]);
  const [filteredAlarms, setFilteredAlarms] = useState([]);
  const [selectedAlarms, setSelectedAlarms] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [severityFilter, setSeverityFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [deviceFilter, setDeviceFilter] = useState('all');
  const [devices, setDevices] = useState([]);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [stats, setStats] = useState({ critical: 0, major: 0, minor: 0, warning: 0, info: 0 });

  const fetchAlarms = useCallback(async () => {
    try {
      const response = await fetch('/api/alarms/');
      const data = await response.json();
      setAlarms(data.alarms || []);
      setDevices([...new Set(data.alarms?.map(a => a.device_name) || [])]);
      calculateStats(data.alarms || []);
    } catch (error) {
      console.error('Error fetching alarms:', error);
    }
  }, []);

  useEffect(() => {
    fetchAlarms();
    const interval = autoRefresh ? setInterval(fetchAlarms, 10000) : null;
    return () => interval && clearInterval(interval);
  }, [fetchAlarms, autoRefresh]);

  useEffect(() => {
    let filtered = [...alarms];
    if (searchTerm) {
      filtered = filtered.filter(a => 
        a.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        a.device_name?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    if (severityFilter !== 'all') {
      filtered = filtered.filter(a => a.severity === severityFilter);
    }
    if (statusFilter !== 'all') {
      filtered = filtered.filter(a => a.status === statusFilter);
    }
    if (deviceFilter !== 'all') {
      filtered = filtered.filter(a => a.device_name === deviceFilter);
    }
    filtered.sort((a, b) => SEVERITY_CONFIG[a.severity]?.priority - SEVERITY_CONFIG[b.severity]?.priority);
    setFilteredAlarms(filtered);
  }, [alarms, searchTerm, severityFilter, statusFilter, deviceFilter]);

  const calculateStats = (alarmList) => {
    const newStats = { critical: 0, major: 0, minor: 0, warning: 0, info: 0 };
    alarmList.forEach(a => { if (newStats[a.severity] !== undefined) newStats[a.severity]++; });
    setStats(newStats);
  };

  const acknowledgeAlarm = async (alarmId) => {
    try {
      await fetch(`/api/alarms/${alarmId}/acknowledge/`, { method: 'POST' });
      fetchAlarms();
    } catch (error) {
      console.error('Error acknowledging alarm:', error);
    }
  };

  const clearAlarm = async (alarmId) => {
    try {
      await fetch(`/api/alarms/${alarmId}/clear/`, { method: 'POST' });
      fetchAlarms();
    } catch (error) {
      console.error('Error clearing alarm:', error);
    }
  };

  const bulkAcknowledge = async () => {
    for (const id of selectedAlarms) {
      await acknowledgeAlarm(id);
    }
    setSelectedAlarms([]);
  };

  const bulkClear = async () => {
    for (const id of selectedAlarms) {
      await clearAlarm(id);
    }
    setSelectedAlarms([]);
  };

  const toggleAlarmSelection = (alarmId) => {
    setSelectedAlarms(prev => 
      prev.includes(alarmId) ? prev.filter(id => id !== alarmId) : [...prev, alarmId]
    );
  };

  const selectAll = () => {
    setSelectedAlarms(filteredAlarms.map(a => a.id));
  };

  const clearSelection = () => {
    setSelectedAlarms([]);
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const SeverityBadge = ({ severity }) => {
    const config = SEVERITY_CONFIG[severity] || SEVERITY_CONFIG.info;
    const Icon = config.icon;
    return (
      <Badge className={`${config.color} text-white flex items-center gap-1`}>
        <Icon className="h-3 w-3" />
        {severity?.toUpperCase()}
      </Badge>
    );
  };

  return (
    <div className="alarm-management-container p-4">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Bell className="h-6 w-6" />
              Alarm Management
            </CardTitle>
            <div className="flex items-center gap-2">
              <Button
                variant={soundEnabled ? "default" : "outline"}
                size="sm"
                onClick={() => setSoundEnabled(!soundEnabled)}
              >
                {soundEnabled ? <Volume2 className="h-4 w-4" /> : <BellOff className="h-4 w-4" />}
              </Button>
              <Button
                variant={autoRefresh ? "default" : "outline"}
                size="sm"
                onClick={() => setAutoRefresh(!autoRefresh)}
              >
                <RefreshCw className={`h-4 w-4 ${autoRefresh ? 'animate-spin' : ''}`} />
              </Button>
              <Button onClick={fetchAlarms} size="sm">
                Refresh
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {/* Stats Summary */}
          <div className="grid grid-cols-5 gap-4 mb-6">
            {Object.entries(stats).map(([severity, count]) => (
              <Card key={severity} className={`${SEVERITY_CONFIG[severity]?.color} bg-opacity-20`}>
                <CardContent className="p-4 text-center">
                  <div className="text-2xl font-bold">{count}</div>
                  <div className="text-sm capitalize">{severity}</div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Filters */}
          <div className="flex flex-wrap gap-4 mb-4">
            <div className="flex items-center gap-2 flex-1 min-w-[200px]">
              <Search className="h-4 w-4 text-gray-500" />
              <Input
                placeholder="Search alarms..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <Select value={severityFilter} onValueChange={setSeverityFilter}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Severity" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Severities</SelectItem>
                <SelectItem value="critical">Critical</SelectItem>
                <SelectItem value="major">Major</SelectItem>
                <SelectItem value="minor">Minor</SelectItem>
                <SelectItem value="warning">Warning</SelectItem>
                <SelectItem value="info">Info</SelectItem>
              </SelectContent>
            </Select>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="acknowledged">Acknowledged</SelectItem>
                <SelectItem value="cleared">Cleared</SelectItem>
              </SelectContent>
            </Select>
            <Select value={deviceFilter} onValueChange={setDeviceFilter}>
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="Device" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Devices</SelectItem>
                {devices.map(device => (
                  <SelectItem key={device} value={device}>{device}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Bulk Actions */}
          {selectedAlarms.length > 0 && (
            <div className="flex items-center gap-4 mb-4 p-2 bg-gray-100 dark:bg-gray-800 rounded">
              <span>{selectedAlarms.length} alarm(s) selected</span>
              <Button onClick={bulkAcknowledge} size="sm" variant="outline">
                Acknowledge Selected
              </Button>
              <Button onClick={bulkClear} size="sm" variant="outline">
                Clear Selected
              </Button>
              <Button onClick={clearSelection} size="sm" variant="ghost">
                Cancel
              </Button>
            </div>
          )}

          {/* Alarms Table */}
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12">
                    <input
                      type="checkbox"
                      checked={selectedAlarms.length === filteredAlarms.length && filteredAlarms.length > 0}
                      onChange={(e) => e.target.checked ? selectAll() : clearSelection()}
                    />
                  </TableHead>
                  <TableHead>Severity</TableHead>
                  <TableHead>Device</TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead>Time</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredAlarms.map(alarm => (
                  <TableRow key={alarm.id} className={alarm.status === 'active' ? 'bg-red-50 dark:bg-red-900/10' : ''}>
                    <TableCell>
                      <input
                        type="checkbox"
                        checked={selectedAlarms.includes(alarm.id)}
                        onChange={() => toggleAlarmSelection(alarm.id)}
                      />
                    </TableCell>
                    <TableCell><SeverityBadge severity={alarm.severity} /></TableCell>
                    <TableCell className="font-medium">{alarm.device_name}</TableCell>
                    <TableCell>{alarm.description}</TableCell>
                    <TableCell className="text-sm text-gray-500">{formatTimestamp(alarm.timestamp)}</TableCell>
                    <TableCell>
                      <Badge variant={alarm.status === 'active' ? 'destructive' : 'secondary'}>
                        {alarm.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        {alarm.status === 'active' && (
                          <Button size="sm" variant="outline" onClick={() => acknowledgeAlarm(alarm.id)}>
                            <CheckCircle className="h-4 w-4" />
                          </Button>
                        )}
                        {alarm.status !== 'cleared' && (
                          <Button size="sm" variant="outline" onClick={() => clearAlarm(alarm.id)}>
                            <XCircle className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AlarmManagement;
