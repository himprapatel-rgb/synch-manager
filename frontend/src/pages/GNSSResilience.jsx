import { Satellite } from 'lucide-react'
export default function GNSSResilience() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">GNSS Resilience</h1>
        <p className="text-gray-400">Satellite constellation monitoring and backup timing</p>
      </div>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {['GPS', 'GLONASS', 'Galileo'].map((sat) => (
          <div key={sat} className="p-4 bg-gray-800 rounded-xl border border-gray-700">
            <Satellite className="w-8 h-8 mb-2 text-cyan-400" />
            <h3 className="font-semibold text-white">{sat}</h3>
            <p className="text-xs text-green-400">Tracking: 12 satellites</p>
          </div>
        ))}
      </div>
    </div>
  )
}
