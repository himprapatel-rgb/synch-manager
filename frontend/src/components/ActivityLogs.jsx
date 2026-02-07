import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Activity, Search, Download, RefreshCw, Filter, User, Settings, AlertTriangle, Shield, Clock, FileText, Database } from 'lucide-react';

const ACTION_ICONS = {
  login: User,
  logout: User,
  create: FileText,
  update: Settings,
  delete: AlertTriangle,
  config_change: Settings,
  alarm_ack: AlertTriangle,
  backup: Database,
  restore: Database,
  firmware: Shield,
  default: Activity
};

const ACTION_COLORS = {
  login: 'bg-green-500',
  logout: 'bg-gray-500',
  create: 'bg-blue-500',
  update: 'bg-yellow-500',
  delete: 'bg-red-500',
  config_change: 'bg-purple-500',
  alarm_ack: 'bg-orange-500',
  backup: 'bg-cyan-500',
  restore: 'bg-indigo-500',
  firmware: 'bg-pink-500',
  default: 'bg-gray-400'
};

const ActivityLogs = () => {
  const [logs, setLogs] = useState([]);
  const [filteredLogs, setFilteredLogs] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [actionFilter, setActionFilter] = useState('all');
  const [userFilter, setUserFilter] = useState('all');
  const [dateRange, setDateRange] = useState('24h');
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pagination, setPagination] = useState({ page: 1, total: 0, perPage: 50 });

  useEffect(() => {
    fetchLogs();
    fetchUsers();
  }, [dateRange, pagination.page]);

  useEffect(() => {
    filterLogs();
  }, [logs, searchTerm, actionFilter, userFilter]);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/activity-logs/?range=${dateRange}&page=${pagination.page}`);
      const data = await response.json();
      setLogs(data.results || []);
      setPagination(prev => ({ ...prev, total: data.count || 0 }));
    } catch (error) {
      console.error('Error fetching logs:', error);
    }
    setLoading(false);
  };

  const fetchUsers = async () => {
    try {
      const response = await fetch('/api/users/');
      const data = await response.json();
      setUsers(data.results || []);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const filterLogs = () => {
    let filtered = [...logs];
    if (searchTerm) {
      filtered = filtered.filter(log =>
        log.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        log.user_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        log.ip_address?.includes(searchTerm)
      );
    }
    if (actionFilter !== 'all') {
      filtered = filtered.filter(log => log.action === actionFilter);
    }
    if (userFilter !== 'all') {
      filtered = filtered.filter(log => log.user_id?.toString() === userFilter);
    }
    setFilteredLogs(filtered);
  };

  const exportLogs = async () => {
    try {
      const response = await fetch(`/api/activity-logs/export/?range=${dateRange}&format=csv`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `activity-logs-${new Date().toISOString().split('T')[0]}.csv`;
      a.click();
    } catch (error) {
      console.error('Error exporting logs:', error);
    }
  };

  const getActionIcon = (action) => {
    const Icon = ACTION_ICONS[action] || ACTION_ICONS.default;
    return Icon;
  };

  const getActionColor = (action) => {
    return ACTION_COLORS[action] || ACTION_COLORS.default;
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  const getRelativeTime = (timestamp) => {
    const now = new Date();
    const then = new Date(timestamp);
    const diff = Math.floor((now - then) / 1000);
    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
  };

  return (
    <div className="activity-logs p-4">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-6 w-6" />
              Activity Logs
            </CardTitle>
            <div className="flex items-center gap-2">
              <Button variant="outline" onClick={exportLogs}>
                <Download className="h-4 w-4 mr-2" />
                Export CSV
              </Button>
              <Button onClick={fetchLogs} disabled={loading}>
                <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {/* Filters */}
          <div className="flex flex-wrap gap-4 mb-6">
            <div className="flex items-center gap-2 flex-1 min-w-[200px]">
              <Search className="h-4 w-4 text-gray-500" />
              <Input
                placeholder="Search logs..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <Select value={dateRange} onValueChange={setDateRange}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Time Range" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1h">Last Hour</SelectItem>
                <SelectItem value="24h">Last 24 Hours</SelectItem>
                <SelectItem value="7d">Last 7 Days</SelectItem>
                <SelectItem value="30d">Last 30 Days</SelectItem>
                <SelectItem value="all">All Time</SelectItem>
              </SelectContent>
            </Select>
            <Select value={actionFilter} onValueChange={setActionFilter}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Action" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Actions</SelectItem>
                <SelectItem value="login">Login</SelectItem>
                <SelectItem value="logout">Logout</SelectItem>
                <SelectItem value="create">Create</SelectItem>
                <SelectItem value="update">Update</SelectItem>
                <SelectItem value="delete">Delete</SelectItem>
                <SelectItem value="config_change">Config Change</SelectItem>
                <SelectItem value="backup">Backup</SelectItem>
                <SelectItem value="firmware">Firmware</SelectItem>
              </SelectContent>
            </Select>
            <Select value={userFilter} onValueChange={setUserFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="User" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Users</SelectItem>
                {users.map(user => (
                  <SelectItem key={user.id} value={user.id.toString()}>{user.username}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-4 gap-4 mb-6">
            <Card className="bg-blue-50 dark:bg-blue-900/20">
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold">{filteredLogs.length}</div>
                <div className="text-sm text-gray-500">Total Events</div>
              </CardContent>
            </Card>
            <Card className="bg-green-50 dark:bg-green-900/20">
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold">{filteredLogs.filter(l => l.action === 'login').length}</div>
                <div className="text-sm text-gray-500">Logins</div>
              </CardContent>
            </Card>
            <Card className="bg-yellow-50 dark:bg-yellow-900/20">
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold">{filteredLogs.filter(l => l.action === 'config_change').length}</div>
                <div className="text-sm text-gray-500">Config Changes</div>
              </CardContent>
            </Card>
            <Card className="bg-red-50 dark:bg-red-900/20">
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold">{filteredLogs.filter(l => l.status === 'failed').length}</div>
                <div className="text-sm text-gray-500">Failed Actions</div>
              </CardContent>
            </Card>
          </div>

          {/* Logs Table */}
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12"></TableHead>
                  <TableHead>Timestamp</TableHead>
                  <TableHead>User</TableHead>
                  <TableHead>Action</TableHead>
                  <TableHead>Description</TableHead>
                  <TableHead>IP Address</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredLogs.map(log => {
                  const Icon = getActionIcon(log.action);
                  return (
                    <TableRow key={log.id}>
                      <TableCell>
                        <div className={`w-8 h-8 rounded-full ${getActionColor(log.action)} flex items-center justify-center`}>
                          <Icon className="h-4 w-4 text-white" />
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="text-sm">{formatTimestamp(log.timestamp)}</div>
                        <div className="text-xs text-gray-500">{getRelativeTime(log.timestamp)}</div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <User className="h-4 w-4" />
                          {log.user_name || 'System'}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className="capitalize">{log.action?.replace('_', ' ')}</Badge>
                      </TableCell>
                      <TableCell className="max-w-xs truncate">{log.description}</TableCell>
                      <TableCell className="font-mono text-sm">{log.ip_address}</TableCell>
                      <TableCell>
                        <Badge variant={log.status === 'success' ? 'default' : 'destructive'}>
                          {log.status}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between mt-4">
            <div className="text-sm text-gray-500">
              Showing {filteredLogs.length} of {pagination.total} entries
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" disabled={pagination.page === 1}
                onClick={() => setPagination(p => ({ ...p, page: p.page - 1 }))}>
                Previous
              </Button>
              <Button variant="outline" size="sm" disabled={pagination.page * pagination.perPage >= pagination.total}
                onClick={() => setPagination(p => ({ ...p, page: p.page + 1 }))}>
                Next
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ActivityLogs;
