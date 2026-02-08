import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Server, Plus, Search, Filter, CheckCircle, XCircle, Clock, ChevronRight } from 'lucide-react'
import Breadcrumb from '../components/Breadcrumb'

export default function Inventory() {
  const navigate = useNavigate()
  const [searchQuery, setSearchQuery] = useState('')
  const [filterType, setFilterType] = useState('all')
  const [filterStatus, setFilterStatus] = useState('all')
  const [showAddModal, setShowAddModal] = useState(false)

  const { data: devices = [], isLoading } = useQuery({
    queryKey: ['network-elements'],
    queryFn: async () => {
      const res = await fetch('https://synch-manager-production.up.railway.app/api/v1/inventory/network-elements/')
      if (!res.ok) return []
      const data = await res.json()
      return data.results || data
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
    const statusLower = status?.toLowerCase()
    if (statusLower === 'managed') return { Icon: CheckCircle, color: 'text-green-400', label: 'Synced' }
    if (statusLower === 'unavailable') return { Icon: XCircle, color: 'text-red-400', label: 'Unavailable' }
    if (statusLower === 'unmanaged') return { Icon: XCircle, color: 'text-gray-400', label: 'Unmanaged' }
    return { Icon: Clock, color: 'text-yellow-400', label: 'Pending' }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
        <Breadcrumb items={[{ label: 'Inventory' }]} />
          <h1 className="text-2xl font-bold text-white">Network Inventory</h1>
          <p className="text-gray-400">Manage PTP/NTP network elements - Click any device for details</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 text-white transition-colors rounded-lg bg-cyan-600 hover:bg-cyan-700" onClick={() => setShowAddModal(true)}>
          <Plus className="w-4 h-4" />Add Device
        </button>
      </div>

      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute w-4 h-4 text-gray-400 transform -translate-y-1/2 left-3 top-1/2" />
          <input type="text" placeholder="Search devices..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full py-2 pl-10 pr-4 text-white bg-gray-800 border border-gray-700 rounded-lg" />
        </div>
        <select value={filterType} onChange={(e) => setFilterType(e.target.value)} className="px-3 py-2 text-white bg-gray-800 border border-gray-700 rounded-lg">
          <option value="all">All Types</option>
          <option value="TimeProvider 4100">TimeProvider 4100</option>
          <option value="TimeProvider 5000">TimeProvider 5000</option>
          <option value="Grandmaster">Grandmaster</option>
        </select>
        <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)} className="px-3 py-2 text-white bg-gray-800 border border-gray-700 rounded-lg">
          <option value="all">All Status</option>
          <option value="Managed">Managed</option>
          <option value="Unmanaged">Unmanaged</option>
        </select>
      </div>

      <div className="overflow-hidden border border-gray-700 rounded-lg">
        <table className="w-full">
          <thead className="bg-gray-800">
            <tr>
              <th className="px-6 py-3 text-xs font-medium tracking-wider text-left text-gray-300 uppercase">Name</th>
              <th className="px-6 py-3 text-xs font-medium tracking-wider text-left text-gray-300 uppercase">IP Address</th>
              <th className="px-6 py-3 text-xs font-medium tracking-wider text-left text-gray-300 uppercase">Type</th>
              <th className="px-6 py-3 text-xs font-medium tracking-wider text-left text-gray-300 uppercase">Status</th>
              <th className="px-6 py-3 text-xs font-medium tracking-wider text-right text-gray-300 uppercase"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700">
            {isLoading ? (
              <tr><td colSpan="5" className="px-6 py-8 text-center text-gray-400"><Clock className="w-5 h-5 mr-2 animate-spin inline" />Loading...</td></tr>
            ) : filteredDevices.length === 0 ? (
              <tr><td colSpan="5" className="px-6 py-8 text-center text-gray-400"><Server className="w-8 h-8 mx-auto mb-2 opacity-50" /><p>No devices found</p></td></tr>
            ) : (
              filteredDevices.map((device) => {
                const statusInfo = getStatusInfo(device.management_state)
                const StatusIcon = statusInfo.Icon
                return (
                  <tr key={device.id} onClick={() => navigate(`/inventory/${device.id}`)} className="transition-colors cursor-pointer hover:bg-gray-800">
                    <td className="px-6 py-4 text-sm font-medium text-white">{device.name}</td>
                    <td className="px-6 py-4 text-sm text-gray-300 font-mono">{device.ip_address}</td>
                    <td className="px-6 py-4 text-sm text-gray-300">{device.ne_type}</td>
                    <td className="px-6 py-4 text-sm"><div className="flex items-center gap-2"><StatusIcon className={`w-4 h-4 ${statusInfo.color}`} /><span className={statusInfo.color}>{statusInfo.label}</span></div></td>
                    <td className="px-6 py-4 text-right"><ChevronRight className="w-5 h-5 text-gray-500" /></td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>

      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold text-white mb-4">Add New Device</h2>
            <form onSubmit={(e) => { e.preventDefault(); setShowAddModal(false); }}>
              <div className="space-y-4">
                <div><label className="block text-sm font-medium text-gray-300 mb-1">Device Name</label><input type="text" required className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white" placeholder="TP4100-01" /></div>
                <div><label className="block text-sm font-medium text-gray-300 mb-1">IP Address</label><input type="text" required className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white" placeholder="192.168.1.100" /></div>
                <div><label className="block text-sm font-medium text-gray-300 mb-1">Device Type</label>
                  <select required className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white">
                    <option value="">Select Type</option>
                    <option value="TimeProvider 4100">TimeProvider 4100</option>
                    <option value="TimeProvider 5000">TimeProvider 5000</option>
                    <option value="Grandmaster">Grandmaster</option>
                  </select>
                </div>
              </div>
              <div className="flex gap-3 mt-6">
                <button type="button" onClick={() => setShowAddModal(false)} className="flex-1 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600">Cancel</button>
                <button type="submit" className="flex-1 px-4 py-2 bg-cyan-600 text-white rounded-lg hover:bg-cyan-700">Add Device</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
