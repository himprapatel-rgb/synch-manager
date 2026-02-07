import { Clock, Zap } from 'lucide-react'
export default function WarMode() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">War Mode</h1>
        <p className="text-gray-400">Tactical timing for mission-critical deployments</p>
      </div>
      <div className="p-6 bg-gray-800 rounded-xl border border-orange-500/50">
        <div className="flex items-center gap-3 mb-4">
          <Zap className="w-8 h-8 text-orange-400" />
          <h2 className="text-lg font-semibold text-orange-400">Tactical Mode Ready</h2>
        </div>
        <p className="text-sm text-gray-400">Quick-deploy timing synchronization for field operations</p>
        <button className="mt-4 px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600">Activate War Mode</button>
      </div>
    </div>
  )
}
