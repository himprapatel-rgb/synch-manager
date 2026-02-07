import { useQuery } from '@tanstack/react-query'
import { Server, Plus, Search } from 'lucide-react'

export default function Inventory() {
  const { data: devices, isLoading } = useQuery({
    queryKey: ['network-elements'],
    queryFn: async () => {
      const res = await fetch('/api/v1/inventory/network-elements/')
      if (!res.ok) return []
      return res.json()
    }
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Network Inventory</h1>
          <p className="text-gray-400">Manage PTP/NTP network elements</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-cyan-500 text-white rounded-lg hover:bg-cyan-600">
          <Plus className="w-4 h-4" />Add Device
        </button>
      </div>

      <div className="flex gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input type="text" placeholder="Search devices..." className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white" />
        </div>
      </div>

      <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-700">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-400">Name</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-400">IP Address</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-400">Type</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-400">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700">
            {isLoading ? (
              <tr><td colSpan="4" className="px-4 py-8 text-center text-gray-400">Loading...</td></tr>
            ) : devices?.results?.length > 0 ? (
              devices.results.map((d) => (
                <tr key={d.id} className="hover:bg-gray-700">
                  <td className="px-4 py-3 text-white">{d.name}</td>
                  <td className="px-4 py-3 text-gray-400">{d.ip_address}</td>
                  <td className="px-4 py-3 text-gray-400">{d.device_type}</td>
                  <td className="px-4 py-3"><span className="px-2 py-1 text-xs rounded-full bg-green-400/10 text-green-400">Online</span></td>
                </tr>
              ))
            ) : (
              <tr><td colSpan="4" className="px-4 py-8 text-center text-gray-400">No devices found</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
