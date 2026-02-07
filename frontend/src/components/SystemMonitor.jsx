import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity, Cpu, HardDrive, MemoryStick, Network, RefreshCw, Server, Thermometer, Clock, Zap } from 'lucide-react';
import './SystemMonitor.css';

const SystemMonitor = () => {
  const [systemData, setSystemData] = useState(null);
  const [history, setHistory] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [devices, setDevices] = useState([]);

  useEffect(() => {
    fetchDevices();
    const interval = setInterval(fetchSystemData, 5000);
    return () => clearInterval(interval);
  }, [selectedDevice]);

  const fetchDevices = async () => {
    try {
      const response = await fetch('/api/devices/');
      const data = await response.json();
      setDevices(data.results || []);
      if (data.results?.length > 0 && !selectedDevice) {
        setSelectedDevice(data.results[0].id);
      }
    } catch (error) {
      console.error('Error fetching devices:', error);
    }
  };

  const fetchSystemData = async () => {
    if (!selectedDevice) return;
    try {
      const response = await fetch(`/api/devices/${selectedDevice}/system-stats/`);
      const data = await response.json();
      setSystemData(data);
      setHistory(prev => {
        const newHistory = [...prev, { ...data, timestamp: new Date().toLocaleTimeString() }];
        return newHistory.slice(-30);
      });
    } catch (error) {
      console.error('Error fetching system data:', error);
    }
  };

  const MetricCard = ({ title, value, icon: Icon, unit, status, progress, color }) => (
    <Card className="metric-card">
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Icon className={`h-5 w-5 ${color || 'text-blue-500'}`} />
            <span className="text-sm text-gray-500">{title}</span>
          </div>
          {status && (
            <Badge variant={status === 'normal' ? 'default' : status === 'warning' ? 'warning' : 'destructive'}>
              {status}
            </Badge>
          )}
        </div>
        <div className="text-2xl font-bold">{value}{unit}</div>
        {progress !== undefined && (
          <Progress value={progress} className="mt-2" />
        )}
      </CardContent>
    </Card>
  );

  const getStatusColor = (value, warning = 70, critical = 90) => {
    if (value >= critical) return 'text-red-500';
    if (value >= warning) return 'text-yellow-500';
    return 'text-green-500';
  };

  const getStatus = (value, warning = 70, critical = 90) => {
    if (value >= critical) return 'critical';
    if (value >= warning) return 'warning';
    return 'normal';
  };

  return (
    <div className="system-monitor-container p-4">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-6 w-6" />
              System Monitor
            </CardTitle>
            <div className="flex items-center gap-4">
              <select
                className="border rounded px-3 py-1 bg-background"
                value={selectedDevice || ''}
                onChange={(e) => setSelectedDevice(e.target.value)}
              >
                {devices.map(device => (
                  <option key={device.id} value={device.id}>{device.name}</option>
                ))}
              </select>
              <button onClick={fetchSystemData} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded">
                <RefreshCw className="h-4 w-4" />
              </button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {/* Overview Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-6">
            <MetricCard
              title="CPU Usage"
              value={systemData?.cpu?.usage || 0}
              unit="%"
              icon={Cpu}
              progress={systemData?.cpu?.usage}
              status={getStatus(systemData?.cpu?.usage || 0)}
              color={getStatusColor(systemData?.cpu?.usage || 0)}
            />
            <MetricCard
              title="Memory"
              value={systemData?.memory?.used_percent || 0}
              unit="%"
              icon={MemoryStick}
              progress={systemData?.memory?.used_percent}
              status={getStatus(systemData?.memory?.used_percent || 0)}
              color={getStatusColor(systemData?.memory?.used_percent || 0)}
            />
            <MetricCard
              title="Disk Usage"
              value={systemData?.disk?.used_percent || 0}
              unit="%"
              icon={HardDrive}
              progress={systemData?.disk?.used_percent}
              status={getStatus(systemData?.disk?.used_percent || 0, 80, 95)}
              color={getStatusColor(systemData?.disk?.used_percent || 0, 80, 95)}
            />
            <MetricCard
              title="Temperature"
              value={systemData?.temperature || 0}
              unit="°C"
              icon={Thermometer}
              status={getStatus(systemData?.temperature || 0, 60, 80)}
              color={getStatusColor(systemData?.temperature || 0, 60, 80)}
            />
            <MetricCard
              title="Uptime"
              value={systemData?.uptime || '0d'}
              unit=""
              icon={Clock}
              color="text-blue-500"
            />
            <MetricCard
              title="Network I/O"
              value={systemData?.network?.throughput || 0}
              unit=" Mbps"
              icon={Network}
              color="text-purple-500"
            />
          </div>

          <Tabs defaultValue="performance" className="w-full">
            <TabsList>
              <TabsTrigger value="performance">Performance</TabsTrigger>
              <TabsTrigger value="processes">Processes</TabsTrigger>
              <TabsTrigger value="network">Network</TabsTrigger>
              <TabsTrigger value="storage">Storage</TabsTrigger>
            </TabsList>

            <TabsContent value="performance" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* CPU Chart */}
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm flex items-center gap-2">
                      <Cpu className="h-4 w-4" /> CPU History
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={200}>
                      <AreaChart data={history}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="timestamp" tick={{ fontSize: 10 }} />
                        <YAxis domain={[0, 100]} />
                        <Tooltip />
                        <Area type="monotone" dataKey="cpu.usage" stroke="#3b82f6" fill="#3b82f680" name="CPU %" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                {/* Memory Chart */}
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm flex items-center gap-2">
                      <MemoryStick className="h-4 w-4" /> Memory History
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={200}>
                      <AreaChart data={history}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="timestamp" tick={{ fontSize: 10 }} />
                        <YAxis domain={[0, 100]} />
                        <Tooltip />
                        <Area type="monotone" dataKey="memory.used_percent" stroke="#22c55e" fill="#22c55e80" name="Memory %" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="processes">
              <Card>
                <CardContent className="p-4">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-2">Process</th>
                        <th className="text-right py-2">PID</th>
                        <th className="text-right py-2">CPU %</th>
                        <th className="text-right py-2">Memory</th>
                        <th className="text-right py-2">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(systemData?.processes || []).slice(0, 10).map((proc, idx) => (
                        <tr key={idx} className="border-b border-gray-100 dark:border-gray-800">
                          <td className="py-2">{proc.name}</td>
                          <td className="text-right">{proc.pid}</td>
                          <td className="text-right">{proc.cpu}%</td>
                          <td className="text-right">{proc.memory}MB</td>
                          <td className="text-right">
                            <Badge variant={proc.status === 'running' ? 'default' : 'secondary'}>
                              {proc.status}
                            </Badge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="network">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card>
                  <CardHeader><CardTitle className="text-sm">Network Interfaces</CardTitle></CardHeader>
                  <CardContent>
                    {(systemData?.network?.interfaces || []).map((iface, idx) => (
                      <div key={idx} className="flex justify-between items-center py-2 border-b">
                        <div>
                          <div className="font-medium">{iface.name}</div>
                          <div className="text-xs text-gray-500">{iface.ip}</div>
                        </div>
                        <Badge variant={iface.status === 'up' ? 'default' : 'destructive'}>
                          {iface.status}
                        </Badge>
                      </div>
                    ))}
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader><CardTitle className="text-sm">Network Throughput</CardTitle></CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={200}>
                      <LineChart data={history}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="timestamp" tick={{ fontSize: 10 }} />
                        <YAxis />
                        <Tooltip />
                        <Line type="monotone" dataKey="network.rx" stroke="#22c55e" name="RX Mbps" />
                        <Line type="monotone" dataKey="network.tx" stroke="#3b82f6" name="TX Mbps" />
                      </LineChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="storage">
              <Card>
                <CardContent className="p-4">
                  {(systemData?.storage?.disks || []).map((disk, idx) => (
                    <div key={idx} className="mb-4">
                      <div className="flex justify-between mb-1">
                        <span className="flex items-center gap-2">
                          <HardDrive className="h-4 w-4" />
                          {disk.mount} ({disk.filesystem})
                        </span>
                        <span>{disk.used} / {disk.total}</span>
                      </div>
                      <Progress value={disk.percent} className={disk.percent > 90 ? 'bg-red-100' : ''} />
                    </div>
                  ))}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};

export default SystemMonitor;
