import { Shield } from 'lucide-react'
export default function Security() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Security</h1>
        <p className="text-gray-400">RBAC, audit logs, and user management</p>
      </div>
      <div className="p-6 bg-gray-800 rounded-xl border border-gray-700">
        <Shield className="w-12 h-12 mb-4 text-green-400" />
        <h2 className="text-lg font-semibold text-white">System Secured</h2>
        <p className="text-sm text-gray-400">All security policies active</p>
      </div>
    </div>
  )
}
