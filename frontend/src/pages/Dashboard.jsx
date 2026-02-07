import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Server, AlertTriangle, Clock, Activity, Calendar, Download, Bell, CheckCircle, XCircle, AlertCircle } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'
import { format, subHours, subDays } from 'date-fns'
import GrafanaPanel from '../components/GrafanaPanel'

const GRAFANA_URL = import.meta.env.VITE_GRAFANA_URL || 'http://localhost:3000'

// Time range options for the time picker
const timeRanges = [
  { label: 'Last 1 Hour', value: '1h', hours: 1 },
  { label: 'Last 6 Hours', value: '6h', hours: 6 },
  { label: 'Last 24 Hours', value: '24h', hours: 24 },
  { label: 'Last 7 Days', value: '7d', hours: 168 },
  { label: 'Last 30 Days', value: '30d', hours: 720 },
]

// Generate mock chart data
const generateChartData = (hours) => {
  const data = []
  const now = new Date()
  for (let i = hours; i >= 0; i--) {
    const time = subHours(now, i)
    data.push({
      time: format(time, hours > 24 ? 'MM/dd' : 'HH:mm'),
      offset: Math.random() * 100 - 50,
      drift: Math.random() * 20 - 10,
      synced: Math.floor(Math.random() * 5) + 95,
    })
  }
  return data
}

// Mock recent events
const recentEvents = [
  { id: 1, type: 'success', message: 'PTP sync established on node-01', time: '2 min ago', icon: CheckCircle },
  { id: 2, type: 'warning', message: 'Clock drift detected on node-03', time: '5 min ago', icon: AlertCircle },
  { id: 3, type: 'error', message: 'GNSS signal lost on node-05', time: '12 min ago', icon: XCircle },
  { id: 4, type: 'success', message: 'Holdover mode exited on node-02', time: '18 min ago', icon: CheckCircle },
  { id: 5, type: 'info', message: 'Configuration backup completed', time: '25 min ago', icon: Bell },
]

export default function Dashboard() {
  const [selectedTimeRange, setSelectedTimeRange] = useState('6h')
  const selectedRange = timeRanges.find(r => r.value === selectedTimeRange)
  const chartData = generateChartData(selectedRange?.hours || 6)

  const { data: stats } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const res = await fetch('/api/v1/inventory/network-elements/')
      if (!res.ok) return { devices: 0, alarms: 0, synced: 0 }
      const data = await res.json()
      return { devices: data.count || 0, alarms: 0, synced: 0 }
    },
    refetchInterval: 30000
  })

  const statCards = [
    { name: 'Network Elements', value: stats?.devices || 0, icon: Server, color: 'cyan', trend: '+2 this week' },
    { name: 'Active Alarms', value: stats?.alarms || 0, icon: AlertTriangle, color: 'red', trend: 'All clear' },
    { name: 'PTP Synced', value: stats?.synced || 0, icon: Clock, color: 'green', trend: '100% sync rate' },
    { name: 'System Health', value: '99.9%', icon: Activity, color: 'purple', trend: 'Uptime: 45d 12h' },
  ]

  return (
    <div className="space-y-6">
      {/* Header with Time Picker */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Dashboard</h1>
          <p className="text-gray-400">Single Pane of Glass - Real-time synchronization monitoring</p>
        </div>
        
        {/* Time Range Picker */}
        <div className="flex items-center gap-3">
          <Calendar className="w-5 h-5 text-gray-400" />
          <select
            value={selectedTimeRange}
            onChange={(e) => setSelectedTimeRange(e.target.value)}
            className="px-4 py-2 text-sm text-white bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent"
          >
            {timeRanges.map((range) => (
              <option key={range.value} value={range.value}>
                {range.label}
              </option>
            ))}
          </select>
          <button className="flex items-center gap-2 px-4 py-2 text-sm text-gray-400 transition-colors border border-gray-700 rounded-lg hover:text-white hover:bg-gray-800">
            <Download className="w-4 h-4" />
            Export
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat) => (
          <div key={stat.name} className="p-4 transition-all bg-gray-800 border border-gray-700 rounded-xl hover:border-gray-600">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400">{stat.name}</p>
                <p className="text-2xl font-bold text-white">{stat.value}</p>
                <p className={`text-xs mt-1 text-${stat.color}-400`}>{stat.trend}</p>
              </div>
              <div className={`p-3 rounded-lg bg-${stat.color}-500/10`}>
                <stat.icon className={`w-8 h-8 text-${stat.color}-400`} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* PTP Clock Offset Chart */}
        <div className="p-4 bg-gray-800 border border-gray-700 rounded-xl">
          <h3 className="mb-4 text-sm font-medium text-white">PTP Clock Offset (ns)</h3>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="offsetGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="time" stroke="#9ca3af" fontSize={12} />
              <YAxis stroke="#9ca3af" fontSize={12} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
                labelStyle={{ color: '#fff' }}
              />
              <Area type="monotone" dataKey="offset" stroke="#06b6d4" fill="url(#offsetGradient)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Sync Status Chart */}
        <div className="p-4 bg-gray-800 border border-gray-700 rounded-xl">
          <h3 className="mb-4 text-sm font-medium text-white">Network Sync Rate (%)</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="time" stroke="#9ca3af" fontSize={12} />
              <YAxis stroke="#9ca3af" fontSize={12} domain={[90, 100]} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
                labelStyle={{ color: '#fff' }}
              />
              <Line type="monotone" dataKey="synced" stroke="#10b981" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Events & Quick Actions Row */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Recent Events */}
        <div className="p-4 bg-gray-800 border border-gray-700 lg:col-span-2 rounded-xl">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-white">Recent Events</h3>
            <button className="text-xs text-cyan-400 hover:text-cyan-300">View All</button>
          </div>
          <div className="space-y-3">
            {recentEvents.map((event) => (
              <div key={event.id} className="flex items-center gap-3 p-3 transition-colors rounded-lg bg-gray-900/50 hover:bg-gray-900">
                <event.icon className={`w-5 h-5 flex-shrink-0 ${
                  event.type === 'success' ? 'text-green-400' :
                  event.type === 'warning' ? 'text-yellow-400' :
                  event.type === 'error' ? 'text-red-400' : 'text-blue-400'
                }`} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-white truncate">{event.message}</p>
                  <p className="text-xs text-gray-500">{event.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* System Status Card */}
        <div className="p-4 bg-gray-800 border border-gray-700 rounded-xl">
          <h3 className="mb-4 text-sm font-medium text-white">System Status</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">PTP Grandmaster</span>
              <span className="flex items-center gap-1 text-sm text-green-400">
                <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                Active
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">GNSS Receiver</span>
              <span className="flex items-center gap-1 text-sm text-green-400">
                <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                Locked
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">NTP Server</span>
              <span className="flex items-center gap-1 text-sm text-green-400">
                <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                Synced
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Holdover Mode</span>
              <span className="text-sm text-gray-400">Standby</span>
            </div>
            <div className="pt-3 mt-3 border-t border-gray-700">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-400">System Uptime</span>
                <span className="text-sm font-medium text-white">45d 12h 34m</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-400">Last Config Change</span>
                <span className="text-sm text-gray-400">3 days ago</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Grafana Embedded Panels */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <GrafanaPanel title="MTIE Performance" panelId={3} dashboardUid="performance" height={300} />
        <GrafanaPanel title="TDEV Analysis" panelId={4} dashboardUid="performance" height={300} />
      </div>
    </div>
  )
}
