import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '@/components/ui/dialog';
import { Archive, Clock, Download, FileText, RefreshCw, RotateCcw, Save, Trash2, Upload, AlertTriangle, CheckCircle } from 'lucide-react';

const ConfigurationBackup = () => {
  const [backups, setBackups] = useState([]);
  const [devices, setDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState('all');
  const [loading, setLoading] = useState(false);
  const [showRestoreDialog, setShowRestoreDialog] = useState(false);
  const [selectedBackup, setSelectedBackup] = useState(null);
  const [schedules, setSchedules] = useState([]);
  const [showScheduleDialog, setShowScheduleDialog] = useState(false);
  const [newSchedule, setNewSchedule] = useState({ device_id: '', frequency: 'daily', time: '00:00' });

  useEffect(() => {
    fetchBackups();
    fetchDevices();
    fetchSchedules();
  }, [selectedDevice]);

  const fetchBackups = async () => {
    try {
      const url = selectedDevice === 'all' ? '/api/backups/' : `/api/backups/?device=${selectedDevice}`;
      const response = await fetch(url);
      const data = await response.json();
      setBackups(data.results || []);
    } catch (error) {
      console.error('Error fetching backups:', error);
    }
  };

  const fetchDevices = async () => {
    try {
      const response = await fetch('/api/devices/');
      const data = await response.json();
      setDevices(data.results || []);
    } catch (error) {
      console.error('Error fetching devices:', error);
    }
  };

  const fetchSchedules = async () => {
    try {
      const response = await fetch('/api/backup-schedules/');
      const data = await response.json();
      setSchedules(data.results || []);
    } catch (error) {
      console.error('Error fetching schedules:', error);
    }
  };

  const createBackup = async (deviceId) => {
    setLoading(true);
    try {
      await fetch('/api/backups/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ device_id: deviceId || selectedDevice })
      });
      fetchBackups();
    } catch (error) {
      console.error('Error creating backup:', error);
    }
    setLoading(false);
  };

  const restoreBackup = async (backupId) => {
    setLoading(true);
    try {
      await fetch(`/api/backups/${backupId}/restore/`, { method: 'POST' });
      setShowRestoreDialog(false);
      setSelectedBackup(null);
    } catch (error) {
      console.error('Error restoring backup:', error);
    }
    setLoading(false);
  };

  const deleteBackup = async (backupId) => {
    try {
      await fetch(`/api/backups/${backupId}/`, { method: 'DELETE' });
      fetchBackups();
    } catch (error) {
      console.error('Error deleting backup:', error);
    }
  };

  const downloadBackup = async (backupId, filename) => {
    try {
      const response = await fetch(`/api/backups/${backupId}/download/`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename || `backup-${backupId}.tar.gz`;
      a.click();
    } catch (error) {
      console.error('Error downloading backup:', error);
    }
  };

  const formatDate = (dateString) => new Date(dateString).toLocaleString();
  const formatSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  return (
    <div className="configuration-backup-container p-4">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Archive className="h-6 w-6" />
                  Configuration Backups
                </CardTitle>
                <div className="flex items-center gap-2">
                  <Select value={selectedDevice} onValueChange={setSelectedDevice}>
                    <SelectTrigger className="w-[200px]">
                      <SelectValue placeholder="Select Device" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Devices</SelectItem>
                      {devices.map(device => (
                        <SelectItem key={device.id} value={device.id.toString()}>{device.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Button onClick={() => createBackup()} disabled={loading || selectedDevice === 'all'}>
                    <Save className="h-4 w-4 mr-2" />
                    Create Backup
                  </Button>
                  <Button variant="outline" onClick={fetchBackups}>
                    <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Device</TableHead>
                    <TableHead>Filename</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead>Size</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {backups.map(backup => (
                    <TableRow key={backup.id}>
                      <TableCell className="font-medium">{backup.device_name}</TableCell>
                      <TableCell><FileText className="h-4 w-4 inline mr-2" />{backup.filename}</TableCell>
                      <TableCell className="text-sm">{formatDate(backup.created_at)}</TableCell>
                      <TableCell>{formatSize(backup.size)}</TableCell>
                      <TableCell>
                        <Badge variant={backup.status === 'completed' ? 'default' : 'destructive'}>
                          {backup.status === 'completed' ? <><CheckCircle className="h-3 w-3 mr-1" /> Complete</> : backup.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          <Button size="sm" variant="ghost" onClick={() => downloadBackup(backup.id, backup.filename)}>
                            <Download className="h-4 w-4" />
                          </Button>
                          <Button size="sm" variant="ghost" onClick={() => { setSelectedBackup(backup); setShowRestoreDialog(true); }}>
                            <RotateCcw className="h-4 w-4" />
                          </Button>
                          <Button size="sm" variant="ghost" className="text-red-500" onClick={() => deleteBackup(backup.id)}>
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </div>

        <div>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Clock className="h-5 w-5" />
                Backup Schedules
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {schedules.map(schedule => (
                  <div key={schedule.id} className="flex items-center justify-between p-3 border rounded">
                    <div>
                      <div className="font-medium">{schedule.device_name}</div>
                      <div className="text-sm text-gray-500 capitalize">{schedule.frequency} at {schedule.time}</div>
                    </div>
                    <Badge variant={schedule.enabled ? 'default' : 'secondary'}>
                      {schedule.enabled ? 'Active' : 'Paused'}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <Dialog open={showRestoreDialog} onOpenChange={setShowRestoreDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-yellow-500" />
              Confirm Restore
            </DialogTitle>
          </DialogHeader>
          <p>Restore backup to <strong>{selectedBackup?.device_name}</strong>?</p>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowRestoreDialog(false)}>Cancel</Button>
            <Button variant="destructive" onClick={() => restoreBackup(selectedBackup?.id)} disabled={loading}>
              {loading ? 'Restoring...' : 'Restore'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ConfigurationBackup;
