import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Server, Plus, Search, Filter, CheckCircle, XCircle, Clock } from 'lucide-react'

const mockDevices = [
  { id: 1, name: 'PTP-GM-01', ip: '192.168.1.100', type: 'Grandmaster', status: 'synced' },
  { id: 2, name: 'BC-NODE-02', ip: '192.168.1.101', type: 'Boundary Clock', status: 'synced' },
  { id: 3, name: 'NTP-SRV-01', ip: '192.168.1.102', type: 'NTP Server', status: 'synced' },
  { id: 4, name: 'BC-NODE-05', ip: '192.168.1.105', type: 'Boundary Clock', status: 'alarm' },
]

export default function Inventory() {
  const [searchQuery, setSearchQuery] = useState('')
  const [filterType, setFilterType] = useState('all')
  const [filterStatus, setFilterStatus] = useState('all')

  const { data: devices = mockDevices, isLoading } = useQuery({
    queryKey: ['network-elements'],
    queryFn: async () => {
      const res = await fetch('/api/v1/inventory/network-elements/')
      if (!res.ok) return mockDevices
      return res.json()
    }
  })

  const filteredDevices = devices.filter(device => {
    if (searchQuery && !device.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
        !device.ip.includes(searchQuery)) return false
    if (filterType !== 'all' && device.type !== filterType) return false
    if (filterStatus !== 'all' && device.status !== filterStatus) return false
    return true
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Network Inventory</h1>
          <p className="text-gray-400">Manage PTP/NTP network elements</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 text-white bg-cyan-600 rounded-lg hover:bg-cyan-700">
          <Plus className="w-4 h-4" />Add Device
        </button>
      </div>

      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute w-4 h-4 text-gray-400 -translate-y-1/2 left-3 top-1/2" />
          <input type="text" placeholder="Search devices..." value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full py-2 pl-10 pr-4 text-white bg-gray-800 border border-gray-700 rounded-lg" />
        </div>
        <select value={filterType} onChange={(e) => setFilterType(e.target.value)}
          className="px-3 py-2 text-white bg-gray-800 border border-gray-700 rounded-lg">
          <option value="all">All Types</option>
          <option value="Grandmaster">Grandmaster</option>
          <option value="Boundary Clock">Boundary Clock</option>
          <option value="NTP Server">NTP Server</option>
        </select>
        <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}
          className="px-3 py-2 text-white bg-gray-800 border border-gray-700 rounded-lg">
          <option value="all">All Status</option>
          <option value="synced">Synced</option>
          <option value="alarm">Alarm</option>
        </select>
      </div>

      <div className="overflow-hidden bg-gray-800 border border-gray-700 rounded-xl">
        <table className="w-full">
          <thead className="bg-gray-900">
            <tr>
              <th className="px-4 py-3 text-xs font-medium text-left text-gray-400">Name</th>
              <th className="px-4 py-3 text-xs font-medium text-left text-gray-400">IP Address</th>
              <th className="px-4 py-3 text-xs font-medium text-left text-gray-400">Type</th>
              <th className="px-4 py-3 text-xs font-medium text-left text-gray-400">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700">
            {isLoading ? (
              <tr><td colSpan={4} className="px-4 py-8 text-center text-gray-400">Loading...</td></tr>
            ) : filteredDevices.length === 0 ? (
              <tr><td colSpan={4} className="px-4 py-8 text-center text-gray-400">No devices found</td></tr>
            ) : (
              filteredDevices.map((device) => (
                <tr key={device.id} className="transition-colors hover:bg-gray-900/50">
                  <td className="px-4 py-3"><span className="text-sm font-medium text-white">{device.name}</span></td>
                  <td className="px-4 py-3"><span className="text-sm text-gray-300">{device.ip}</span></td>
                  <td className="px-4 py-3"><span className="text-sm text-gray-300">{device.type}</span></td>
                  <td className="px-4 py-3">
                    {device.status === 'synced' ? (
                      <span className="inline-flex items-center gap-1 px-2 py-1 text-xs text-green-400 rounded-full bg-green-500/10">
                        <CheckCircle className="w-3 h-3" />Synced
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2 py-1 text-xs text-red-400 rounded-full bg-red-500/10">
                        <XCircle className="w-3 h-3" />Alarm
                      </span>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
