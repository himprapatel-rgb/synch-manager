import { AlertTriangle } from 'lucide-react'

export default function Alarms() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Alarm Management</h1>
        <p className="text-gray-400">Monitor and manage SNMP traps and alarms</p>
      </div>
      <div className="p-8 bg-gray-800 rounded-xl border border-gray-700 text-center">
        <AlertTriangle className="w-12 h-12 mx-auto mb-4 text-green-400" />
        <p className="text-lg text-white">No active alarms</p>
        <p className="text-sm text-gray-400">All systems operating normally</p>
      </div>
    </div>
  )
}
