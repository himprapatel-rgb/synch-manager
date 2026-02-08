import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, Server, Clock, Wifi, Settings, AlertTriangle, CheckCircle, Activity, Cpu, HardDrive, Network, RefreshCw, Terminal, Download, Upload } from 'lucide-react'

export default function NetworkElementDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('overview')

  const { data: device, isLoading } = useQuery({
    queryKey: ['network-element', id],
    queryFn: async () => {
      const res = await fetch(`https://synch-manager-production.up.railway.app/api/v1/inventory/network-elements/${id}/`)
      if (!res.ok) return null
      return res.json()
    }
  })

  // Mock detailed data - in production from API
  const mockDetails = {
    ptp: { clockClass: 6, clockAccuracy: '0x21', priority1: 128, priority2: 128, domain: 0, offsetFromMaster: '+12ns', meanPathDelay: '245ns' },
    gnss: { status: 'Tracking', satellites: 12, hdop: 0.8, position: '53.2167° N, 6.1000° W', antenna: 'OK' },
    interfaces: [
      { name: 'eth0', status: 'up', speed: '1Gbps', mac: '00:1A:2B:3C:4D:5E', ip: device?.ip_address || '192.168.1.100' },
      { name: 'eth1', status: 'up', speed: '1Gbps', mac: '00:1A:2B:3C:4D:5F', ip: '10.0.0.1' },
      { name: 'ptp0', status: 'up', speed: '1Gbps', mac: '00:1A:2B:3C:4D:60', ip: 'N/A' }
    ],
    alarms: [
      { id: 1, severity: 'warning', message: 'Clock drift detected', timestamp: '2 hours ago' },
      { id: 2, severity: 'cleared', message: 'GNSS signal restored', timestamp: '5 hours ago' }
    ],
    performance: { cpu: 23, memory: 45, uptime: '45d 12h 34m', temperature: '42°C' }
  }

  if (isLoading) return <div className="flex items-center justify-center h-64 text-gray-400"><RefreshCw className="w-6 h-6 animate-spin mr-2" />Loading...</div>

  const tabs = ['overview', 'ptp', 'gnss', 'interfaces', 'alarms', 'performance']

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button onClick={() => navigate('/inventory')} className="p-2 hover:bg-gray-800 rounded-lg"><ArrowLeft className="w-5 h-5 text-gray-400" /></button>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-white">{device?.name || 'Network Element'}</h1>
          <p className="text-gray-400">{device?.ip_address} • {device?.ne_type}</p>
        </div>
        <span className={`px-3 py-1 rounded-full text-sm ${device?.management_state === 'Managed' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'}`}>
          {device?.management_state || 'Unknown'}
        </span>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 p-1 bg-gray-800 rounded-lg">
        {tabs.map(tab => (
          <button key={tab} onClick={() => setActiveTab(tab)} className={`px-4 py-2 rounded-md text-sm font-medium capitalize transition-colors ${activeTab === tab ? 'bg-cyan-600 text-white' : 'text-gray-400 hover:text-white'}`}>{tab}</button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="grid gap-6">
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 bg-gray-800 rounded-lg border border-gray-700">
              <div className="flex items-center gap-3 mb-2"><Server className="w-5 h-5 text-cyan-400" /><span className="text-gray-400">Device Type</span></div>
              <p className="text-xl font-semibold text-white">{device?.ne_type || 'Unknown'}</p>
            </div>
            <div className="p-4 bg-gray-800 rounded-lg border border-gray-700">
              <div className="flex items-center gap-3 mb-2"><Clock className="w-5 h-5 text-green-400" /><span className="text-gray-400">Uptime</span></div>
              <p className="text-xl font-semibold text-white">{mockDetails.performance.uptime}</p>
            </div>
            <div className="p-4 bg-gray-800 rounded-lg border border-gray-700">
              <div className="flex items-center gap-3 mb-2"><Cpu className="w-5 h-5 text-yellow-400" /><span className="text-gray-400">CPU Usage</span></div>
              <p className="text-xl font-semibold text-white">{mockDetails.performance.cpu}%</p>
            </div>
            <div className="p-4 bg-gray-800 rounded-lg border border-gray-700">
              <div className="flex items-center gap-3 mb-2"><Activity className="w-5 h-5 text-purple-400" /><span className="text-gray-400">Temperature</span></div>
              <p className="text-xl font-semibold text-white">{mockDetails.performance.temperature}</p>
            </div>
          </div>
        )}

        {activeTab === 'ptp' && (
          <div className="p-6 bg-gray-800 rounded-lg border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-4">PTP Configuration</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(mockDetails.ptp).map(([key, value]) => (
                <div key={key} className="p-3 bg-gray-900 rounded">
                  <p className="text-xs text-gray-500 uppercase">{key.replace(/([A-Z])/g, ' $1')}</p>
                  <p className="text-white font-mono">{value}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'gnss' && (
          <div className="p-6 bg-gray-800 rounded-lg border border-gray-700">
            <h3 className="text-lg font-semibold text-white mb-4">GNSS Status</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {Object.entries(mockDetails.gnss).map(([key, value]) => (
                <div key={key} className="p-3 bg-gray-900 rounded">
                  <p className="text-xs text-gray-500 uppercase">{key}</p>
                  <p className="text-white">{value}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'interfaces' && (
          <div className="overflow-hidden border border-gray-700 rounded-lg">
            <table className="w-full">
              <thead className="bg-gray-800"><tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Interface</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Status</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Speed</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">MAC</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">IP</th>
              </tr></thead>
              <tbody className="divide-y divide-gray-700">
                {mockDetails.interfaces.map(iface => (
                  <tr key={iface.name} className="hover:bg-gray-800">
                    <td className="px-4 py-3 text-white font-mono">{iface.name}</td>
                    <td className="px-4 py-3"><span className={`px-2 py-1 rounded text-xs ${iface.status === 'up' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>{iface.status}</span></td>
                    <td className="px-4 py-3 text-gray-300">{iface.speed}</td>
                    <td className="px-4 py-3 text-gray-300 font-mono text-sm">{iface.mac}</td>
                    <td className="px-4 py-3 text-gray-300">{iface.ip}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'alarms' && (
          <div className="space-y-3">
            {mockDetails.alarms.map(alarm => (
              <div key={alarm.id} className={`p-4 rounded-lg border ${alarm.severity === 'warning' ? 'bg-yellow-500/10 border-yellow-500/30' : 'bg-green-500/10 border-green-500/30'}`}>
                <div className="flex items-center gap-3">
                  {alarm.severity === 'warning' ? <AlertTriangle className="w-5 h-5 text-yellow-400" /> : <CheckCircle className="w-5 h-5 text-green-400" />}
                  <div className="flex-1"><p className="text-white">{alarm.message}</p><p className="text-sm text-gray-400">{alarm.timestamp}</p></div>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'performance' && (
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-gray-800 rounded-lg border border-gray-700">
              <p className="text-gray-400 mb-2">CPU Usage</p>
              <div className="h-4 bg-gray-700 rounded-full overflow-hidden"><div className="h-full bg-cyan-500" style={{width: `${mockDetails.performance.cpu}%`}} /></div>
              <p className="text-right text-white mt-1">{mockDetails.performance.cpu}%</p>
            </div>
            <div className="p-4 bg-gray-800 rounded-lg border border-gray-700">
              <p className="text-gray-400 mb-2">Memory Usage</p>
              <div className="h-4 bg-gray-700 rounded-full overflow-hidden"><div className="h-full bg-purple-500" style={{width: `${mockDetails.performance.memory}%`}} /></div>
              <p className="text-right text-white mt-1">{mockDetails.performance.memory}%</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
