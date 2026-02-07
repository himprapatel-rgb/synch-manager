import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Upload, Download, RefreshCw, CheckCircle, AlertTriangle, Clock, HardDrive, Cpu, Play, Pause, XCircle } from 'lucide-react';

const FirmwareManagement = () => {
  const [devices, setDevices] = useState([]);
  const [firmwareList, setFirmwareList] = useState([]);
  const [upgrades, setUpgrades] = useState([]);
  const [selectedDevices, setSelectedDevices] = useState([]);
  const [selectedFirmware, setSelectedFirmware] = useState(null);
  const [showUpgradeDialog, setShowUpgradeDialog] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchDevices();
    fetchFirmwareList();
    fetchUpgradeHistory();
    const interval = setInterval(fetchUpgradeHistory, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchDevices = async () => {
    try {
      const response = await fetch('/api/devices/');
      const data = await response.json();
      setDevices(data.results || []);
    } catch (error) {
      console.error('Error fetching devices:', error);
    }
  };

  const fetchFirmwareList = async () => {
    try {
      const response = await fetch('/api/firmware/');
      const data = await response.json();
      setFirmwareList(data.results || []);
    } catch (error) {
      console.error('Error fetching firmware:', error);
    }
  };

  const fetchUpgradeHistory = async () => {
    try {
      const response = await fetch('/api/firmware/upgrades/');
      const data = await response.json();
      setUpgrades(data.results || []);
    } catch (error) {
      console.error('Error fetching upgrades:', error);
    }
  };

  const startUpgrade = async () => {
    if (!selectedFirmware || selectedDevices.length === 0) return;
    setLoading(true);
    try {
      await fetch('/api/firmware/upgrade/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          firmware_id: selectedFirmware,
          device_ids: selectedDevices
        })
      });
      setShowUpgradeDialog(false);
      setSelectedDevices([]);
      setSelectedFirmware(null);
      fetchUpgradeHistory();
    } catch (error) {
      console.error('Error starting upgrade:', error);
    }
    setLoading(false);
  };

  const cancelUpgrade = async (upgradeId) => {
    try {
      await fetch(`/api/firmware/upgrades/${upgradeId}/cancel/`, { method: 'POST' });
      fetchUpgradeHistory();
    } catch (error) {
      console.error('Error cancelling upgrade:', error);
    }
  };

  const getStatusBadge = (status) => {
    const configs = {
      pending: { color: 'bg-yellow-500', icon: Clock },
      in_progress: { color: 'bg-blue-500', icon: RefreshCw },
      completed: { color: 'bg-green-500', icon: CheckCircle },
      failed: { color: 'bg-red-500', icon: XCircle },
      cancelled: { color: 'bg-gray-500', icon: XCircle }
    };
    const config = configs[status] || configs.pending;
    const Icon = config.icon;
    return (
      <Badge className={`${config.color} text-white flex items-center gap-1`}>
        <Icon className="h-3 w-3" />
        {status?.replace('_', ' ').toUpperCase()}
      </Badge>
    );
  };

  const toggleDeviceSelection = (deviceId) => {
    setSelectedDevices(prev =>
      prev.includes(deviceId) ? prev.filter(id => id !== deviceId) : [...prev, deviceId]
    );
  };

  return (
    <div className="firmware-management p-4">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <HardDrive className="h-6 w-6" />
              Firmware Management
            </CardTitle>
            <div className="flex gap-2">
              <Button variant="outline" onClick={fetchFirmwareList}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
              <Button onClick={() => setShowUpgradeDialog(true)} disabled={selectedDevices.length === 0}>
                <Upload className="h-4 w-4 mr-2" />
                Upgrade Selected ({selectedDevices.length})
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="devices">
            <TabsList>
              <TabsTrigger value="devices">Devices</TabsTrigger>
              <TabsTrigger value="firmware">Firmware Library</TabsTrigger>
              <TabsTrigger value="history">Upgrade History</TabsTrigger>
            </TabsList>

            <TabsContent value="devices">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-12">
                      <input type="checkbox" onChange={(e) => {
                        if (e.target.checked) setSelectedDevices(devices.map(d => d.id));
                        else setSelectedDevices([]);
                      }} />
                    </TableHead>
                    <TableHead>Device Name</TableHead>
                    <TableHead>Model</TableHead>
                    <TableHead>Current Version</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Last Updated</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {devices.map(device => (
                    <TableRow key={device.id}>
                      <TableCell>
                        <input type="checkbox" checked={selectedDevices.includes(device.id)}
                          onChange={() => toggleDeviceSelection(device.id)} />
                      </TableCell>
                      <TableCell className="font-medium">{device.name}</TableCell>
                      <TableCell>{device.model}</TableCell>
                      <TableCell><Badge variant="outline">{device.firmware_version || 'Unknown'}</Badge></TableCell>
                      <TableCell>{getStatusBadge(device.status)}</TableCell>
                      <TableCell className="text-sm text-gray-500">
                        {device.last_firmware_update ? new Date(device.last_firmware_update).toLocaleDateString() : 'Never'}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TabsContent>

            <TabsContent value="firmware">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {firmwareList.map(fw => (
                  <Card key={fw.id} className="cursor-pointer hover:border-blue-500"
                    onClick={() => setSelectedFirmware(fw.id)}>
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="font-bold">{fw.version}</h3>
                          <p className="text-sm text-gray-500">{fw.device_type}</p>
                        </div>
                        <Badge variant={fw.is_latest ? 'default' : 'secondary'}>
                          {fw.is_latest ? 'Latest' : 'Archive'}
                        </Badge>
                      </div>
                      <div className="mt-3 text-sm">
                        <p><strong>Released:</strong> {new Date(fw.release_date).toLocaleDateString()}</p>
                        <p><strong>Size:</strong> {(fw.size / 1024 / 1024).toFixed(2)} MB</p>
                        <p className="mt-2 text-gray-600 line-clamp-2">{fw.release_notes}</p>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="history">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Device</TableHead>
                    <TableHead>From Version</TableHead>
                    <TableHead>To Version</TableHead>
                    <TableHead>Progress</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Started</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {upgrades.map(upgrade => (
                    <TableRow key={upgrade.id}>
                      <TableCell className="font-medium">{upgrade.device_name}</TableCell>
                      <TableCell>{upgrade.from_version}</TableCell>
                      <TableCell>{upgrade.to_version}</TableCell>
                      <TableCell className="w-32">
                        <Progress value={upgrade.progress} className="h-2" />
                        <span className="text-xs">{upgrade.progress}%</span>
                      </TableCell>
                      <TableCell>{getStatusBadge(upgrade.status)}</TableCell>
                      <TableCell className="text-sm">{new Date(upgrade.started_at).toLocaleString()}</TableCell>
                      <TableCell>
                        {upgrade.status === 'in_progress' && (
                          <Button size="sm" variant="ghost" onClick={() => cancelUpgrade(upgrade.id)}>
                            <XCircle className="h-4 w-4 text-red-500" />
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      <Dialog open={showUpgradeDialog} onOpenChange={setShowUpgradeDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Start Firmware Upgrade</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <p>{selectedDevices.length} device(s) selected for upgrade</p>
            <Select value={selectedFirmware} onValueChange={setSelectedFirmware}>
              <SelectTrigger><SelectValue placeholder="Select firmware version" /></SelectTrigger>
              <SelectContent>
                {firmwareList.map(fw => (
                  <SelectItem key={fw.id} value={fw.id}>{fw.version} - {fw.device_type}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowUpgradeDialog(false)}>Cancel</Button>
            <Button onClick={startUpgrade} disabled={!selectedFirmware || loading}>
              {loading ? 'Starting...' : 'Start Upgrade'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default FirmwareManagement;
