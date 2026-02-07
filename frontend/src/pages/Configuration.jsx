import { Settings } from 'lucide-react'

export default function Configuration() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Configuration</h1>
        <p className="text-gray-400">Manage PTP/NTP profiles and policies</p>
      </div>
      <div className="p-6 bg-gray-800 rounded-xl border border-gray-700">
        <Settings className="w-12 h-12 mb-4 text-cyan-400" />
        <h2 className="text-lg font-semibold text-white">Configuration Profiles</h2>
        <p className="text-sm text-gray-400">Create and manage device configuration templates</p>
      </div>
    </div>
  )
}
