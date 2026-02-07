import { useQuery } from '@tanstack/react-query'
import { Server, AlertTriangle, Clock, Activity } from 'lucide-react'
import GrafanaPanel from '../components/GrafanaPanel'

const GRAFANA_URL = import.meta.env.VITE_GRAFANA_URL || 'http://localhost:3000'

export default function Dashboard() {
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
    { name: 'Network Elements', value: stats?.devices || 0, icon: Server, color: 'cyan' },
    { name: 'Active Alarms', value: stats?.alarms || 0, icon: AlertTriangle, color: 'red' },
    { name: 'PTP Synced', value: stats?.synced || 0, icon: Clock, color: 'green' },
    { name: 'System Health', value: '99.9%', icon: Activity, color: 'purple' },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <p className="text-gray-400">Single Pane of Glass - Real-time synchronization monitoring</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat) => (
          <div key={stat.name} className="p-4 bg-gray-800 rounded-xl border border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400">{stat.name}</p>
                <p className="text-2xl font-bold text-white">{stat.value}</p>
              </div>
              <stat.icon className={`w-10 h-10 text-${stat.color}-400 opacity-50`} />
            </div>
          </div>
        ))}
      </div>

      {/* Grafana Embedded Panels - Single Pane of Glass */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <GrafanaPanel title="PTP Clock Offset" panelId={1} dashboardUid="timing" height={300} />
        <GrafanaPanel title="Network Sync Status" panelId={2} dashboardUid="timing" height={300} />
        <GrafanaPanel title="MTIE Performance" panelId={3} dashboardUid="performance" height={300} />
        <GrafanaPanel title="TDEV Analysis" panelId={4} dashboardUid="performance" height={300} />
      </div>

      {/* Full Grafana Dashboard Embed */}
      <div className="p-4 bg-gray-800 rounded-xl border border-gray-700">
        <h2 className="mb-4 text-lg font-semibold text-white">Performance Overview</h2>
        <iframe
          src={`${GRAFANA_URL}/d/timing/timing-dashboard?orgId=1&kiosk&theme=dark`}
          className="w-full h-[500px] rounded-lg border-0"
          title="Grafana Dashboard"
        />
      </div>
    </div>
  )
}
