import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Server, Plus, Search, Filter, CheckCircle, XCircle, Clock } from 'lucide-react'

export default function Inventory() {
  const [searchQuery, setSearchQuery] = useState('')
  const [filterType, setFilterType] = useState('all')
  const [filterStatus, setFilterStatus] = useState('all')

  const { data: devices = [], isLoading } = useQuery({
    queryKey: ['network-elements'],
    queryFn: async () => {
      const res = await fetch('https://synch-manager-production.up.railway.app/api/v1/inventory/network-elements/')
      if (!res.ok) throw new Error('Failed to fetch')
      return res.json()
    }
  })

  const filteredDevices = devices.filter(device => {
    if (searchQuery && !device.name.toLowerCase().includes(searchQuery.toLowerCase()) && 
        !device.ip_address.includes(searchQuery)) return false
    if (filterType !== 'all' && device.ne_type !== filterType) return false
    if (filterStatus !== 'all' && device.management_state !== filterStatus) return false
    return true
  })

  const getStatusInfo = (status) => {
    switch(status?.toLowerCase()) {
      case 'managed':
        return { icon: CheckCircle, color: 'text-green-400', bg: 'bg-green-400/10', label: 'Synced' }
      case 'unmanaged':
        return { icon: XCircle, color: 'text-gray-400', bg: 'bg-gray-400/10', label: 'Unmanaged' }
      case 'unavailable':
        return { icon: XCircle, color: 'text-red-400', bg: 'bg-red-400/10', label: 'Unavailable' }
      default:
        return { icon: Clock, color: 'text-yellow-400', bg: 'bg-yellow-400/10', label: 'Pending' }
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Network Inventory</h1>
            <p className="text-gray-400">Loading network elements...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Network Inventory</h1>
          <p className="text-gray-400">Manage PTP/NTP network elements</p>
        </div>
        <button className="px-4 py-2 bg-cyan-500 hover:bg-cyan-600 rounded-lg text-white flex items-center gap-2 transition-colors">
          <Plus className="w-5 h-5" />
          Add Device
        </button>
      </div>

      <div className="flex items-center justify-between gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search devices..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-gray-800/50 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-cyan-500"
          />
        </div>
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="px-4 py-2 bg-gray-800/50 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-cyan-500"
        >
          <option value="all">All Types</option>
          <option value="TimeProvider 4100">TimeProvider 4100</option>
          <option value="TimeProvider 5000">TimeProvider 5000</option>
          <option value="Generic PTP Grandmaster">Grandmaster</option>
          <option value="Generic PTP Boundary Clock">Boundary Clock</option>
          <option value="NTP Server">NTP Server</option>
        </select>
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="px-4 py-2 bg-gray-800/50 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-cyan-500"
        >
          <option value="all">All Status</option>
          <option value="Managed">Managed</option>
          <option value="Unmanaged">Unmanaged</option>
          <option value="Unavailable">Unavailable</option>
        </select>
      </div>

      <div className="bg-gray-800/30 rounded-lg border border-gray-700 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-800/50">
            <tr className="border-b border-gray-700">
              <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Name</th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">IP Address</th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Type</th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Status</th>
            </tr>
          </thead>
          <tbody>
            {filteredDevices.length === 0 ? (
              <tr>
                <td colSpan="4" className="px-6 py-8 text-center text-gray-400">
                  <Server className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p>No devices found</p>
                </td>
              </tr>
            ) : (
              filteredDevices.map((device) => {
                const statusInfo = getStatusInfo(device.management_state)
                const StatusIcon = statusInfo.icon
                return (
                  <tr key={device.id} className="border-b border-gray-700/50 hover:bg-gray-800/30 transition-colors">
                    <td className="px-6 py-4 text-white font-medium">{device.name}</td>
                    <td className="px-6 py-4 text-gray-300">{device.ip_address}</td>
                    <td className="px-6 py-4 text-gray-300">{device.ne_type}</td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm ${statusInfo.bg} ${statusInfo.color}`}>
                        <StatusIcon className="w-4 h-4" />
                        {statusInfo.label}
                      </span>
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
