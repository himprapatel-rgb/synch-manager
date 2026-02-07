import { useState } from 'react'
import { AlertTriangle, CheckCircle, XCircle, Clock, Filter, Search, Bell, BellOff, RefreshCw, ChevronDown } from 'lucide-react'
import { format } from 'date-fns'

// Mock alarm data
const mockAlarms = [
  { id: 1, severity: 'critical', source: 'PTP-GM-01', message: 'Grandmaster clock lost GNSS lock', timestamp: new Date(Date.now() - 300000), acknowledged: false, category: 'timing' },
  { id: 2, severity: 'major', source: 'NTP-SRV-02', message: 'Stratum level degraded to 4', timestamp: new Date(Date.now() - 600000), acknowledged: false, category: 'ntp' },
  { id: 3, severity: 'minor', source: 'BC-NODE-05', message: 'Boundary clock offset exceeds threshold', timestamp: new Date(Date.now() - 900000), acknowledged: true, category: 'ptp' },
  { id: 4, severity: 'warning', source: 'GNSS-RCV-01', message: 'Satellite count below optimal (6/12)', timestamp: new Date(Date.now() - 1200000), acknowledged: false, category: 'gnss' },
  { id: 5, severity: 'critical', source: 'BC-NODE-03', message: 'PTP sync lost - entering holdover', timestamp: new Date(Date.now() - 1500000), acknowledged: false, category: 'ptp' },
]

const severityConfig = {
  critical: { color: 'red', icon: XCircle, bg: 'bg-red-500/10', text: 'text-red-400', border: 'border-red-500/50' },
  major: { color: 'orange', icon: AlertTriangle, bg: 'bg-orange-500/10', text: 'text-orange-400', border: 'border-orange-500/50' },
  minor: { color: 'yellow', icon: AlertTriangle, bg: 'bg-yellow-500/10', text: 'text-yellow-400', border: 'border-yellow-500/50' },
  warning: { color: 'blue', icon: Bell, bg: 'bg-blue-500/10', text: 'text-blue-400', border: 'border-blue-500/50' },
}

const categories = ['all', 'timing', 'ptp', 'ntp', 'gnss']

export default function Alarms() {
  const [alarms, setAlarms] = useState(mockAlarms)
  const [selectedSeverity, setSelectedSeverity] = useState('all')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [showAcknowledged, setShowAcknowledged] = useState(true)

  const filteredAlarms = alarms.filter(alarm => {
    if (selectedSeverity !== 'all' && alarm.severity !== selectedSeverity) return false
    if (selectedCategory !== 'all' && alarm.category !== selectedCategory) return false
    if (!showAcknowledged && alarm.acknowledged) return false
    if (searchQuery && !alarm.message.toLowerCase().includes(searchQuery.toLowerCase()) && 
        !alarm.source.toLowerCase().includes(searchQuery.toLowerCase())) return false
    return true
  })

  const handleAcknowledge = (id) => {
    setAlarms(alarms.map(a => a.id === id ? { ...a, acknowledged: true } : a))
  }

  const handleAcknowledgeAll = () => {
    setAlarms(alarms.map(a => ({ ...a, acknowledged: true })))
  }

  const alarmCounts = {
    critical: alarms.filter(a => a.severity === 'critical' && !a.acknowledged).length,
    major: alarms.filter(a => a.severity === 'major' && !a.acknowledged).length,
    minor: alarms.filter(a => a.severity === 'minor' && !a.acknowledged).length,
    warning: alarms.filter(a => a.severity === 'warning' && !a.acknowledged).length,
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Alarm Management</h1>
          <p className="text-gray-400">Monitor and manage SNMP traps and alarms</p>
        </div>
        <div className="flex items-center gap-2">
          <button 
            onClick={handleAcknowledgeAll}
            className="flex items-center gap-2 px-4 py-2 text-sm text-white transition-colors bg-cyan-600 rounded-lg hover:bg-cyan-700"
          >
            <CheckCircle className="w-4 h-4" />
            Acknowledge All
          </button>
          <button className="flex items-center gap-2 px-4 py-2 text-sm text-gray-400 transition-colors border border-gray-700 rounded-lg hover:text-white hover:bg-gray-800">
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>
      </div>

      {/* Severity Summary Cards */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {Object.entries(severityConfig).map(([severity, config]) => {
          const Icon = config.icon
          return (
            <button
              key={severity}
              onClick={() => setSelectedSeverity(selectedSeverity === severity ? 'all' : severity)}
              className={`p-4 rounded-xl border transition-all ${config.bg} ${config.border} ${
                selectedSeverity === severity ? 'ring-2 ring-offset-2 ring-offset-gray-900 ring-' + config.color + '-500' : ''
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400 capitalize">{severity}</p>
                  <p className={`text-2xl font-bold ${config.text}`}>{alarmCounts[severity]}</p>
                </div>
                <Icon className={`w-8 h-8 ${config.text} opacity-50`} />
              </div>
            </button>
          )
        })}
      </div>

      {/* Filters Row */}
      <div className="flex flex-col gap-4 p-4 bg-gray-800 border border-gray-700 rounded-xl sm:flex-row sm:items-center">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute w-4 h-4 text-gray-400 -translate-y-1/2 left-3 top-1/2" />
          <input
            type="text"
            placeholder="Search alarms..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full py-2 pl-10 pr-4 text-white bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
          />
        </div>

        {/* Category Filter */}
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gray-400" />
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-3 py-2 text-sm text-white bg-gray-900 border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
          >
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat === 'all' ? 'All Categories' : cat.toUpperCase()}</option>
            ))}
          </select>
        </div>

        {/* Show Acknowledged Toggle */}
        <button
          onClick={() => setShowAcknowledged(!showAcknowledged)}
          className={`flex items-center gap-2 px-3 py-2 text-sm rounded-lg border transition-colors ${
            showAcknowledged 
              ? 'text-cyan-400 border-cyan-500/50 bg-cyan-500/10' 
              : 'text-gray-400 border-gray-700 hover:text-white'
          }`}
        >
          {showAcknowledged ? <Bell className="w-4 h-4" /> : <BellOff className="w-4 h-4" />}
          {showAcknowledged ? 'Showing All' : 'Hide Acknowledged'}
        </button>
      </div>

      {/* Alarms Table */}
      <div className="overflow-hidden bg-gray-800 border border-gray-700 rounded-xl">
        <table className="w-full">
          <thead className="bg-gray-900">
            <tr>
              <th className="px-4 py-3 text-xs font-medium text-left text-gray-400">Severity</th>
              <th className="px-4 py-3 text-xs font-medium text-left text-gray-400">Source</th>
              <th className="px-4 py-3 text-xs font-medium text-left text-gray-400">Message</th>
              <th className="px-4 py-3 text-xs font-medium text-left text-gray-400">Time</th>
              <th className="px-4 py-3 text-xs font-medium text-left text-gray-400">Status</th>
              <th className="px-4 py-3 text-xs font-medium text-left text-gray-400">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700">
            {filteredAlarms.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-12 text-center">
                  <AlertTriangle className="w-12 h-12 mx-auto mb-4 text-green-400" />
                  <p className="text-lg text-white">No active alarms</p>
                  <p className="text-sm text-gray-400">All systems operating normally</p>
                </td>
              </tr>
            ) : (
              filteredAlarms.map((alarm) => {
                const config = severityConfig[alarm.severity]
                const Icon = config.icon
                return (
                  <tr key={alarm.id} className={`transition-colors hover:bg-gray-900/50 ${alarm.acknowledged ? 'opacity-60' : ''}`}>
                    <td className="px-4 py-3">
                      <div className={`inline-flex items-center gap-2 px-2 py-1 rounded-full ${config.bg}`}>
                        <Icon className={`w-4 h-4 ${config.text}`} />
                        <span className={`text-xs font-medium capitalize ${config.text}`}>{alarm.severity}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm font-medium text-white">{alarm.source}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm text-gray-300">{alarm.message}</span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-1 text-sm text-gray-400">
                        <Clock className="w-4 h-4" />
                        {format(alarm.timestamp, 'HH:mm:ss')}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      {alarm.acknowledged ? (
                        <span className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-green-400 rounded-full bg-green-500/10">
                          <CheckCircle className="w-3 h-3" />
                          Acknowledged
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium text-red-400 rounded-full bg-red-500/10">
                          <Bell className="w-3 h-3" />
                          Active
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      {!alarm.acknowledged && (
                        <button
                          onClick={() => handleAcknowledge(alarm.id)}
                          className="px-3 py-1 text-xs text-cyan-400 transition-colors border rounded-lg border-cyan-500/50 hover:bg-cyan-500/10"
                        >
                          Acknowledge
                        </button>
                      )}
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Alarm History Link */}
      <div className="flex items-center justify-between p-4 bg-gray-800 border border-gray-700 rounded-xl">
        <div>
          <h3 className="text-sm font-medium text-white">Alarm History</h3>
          <p className="text-xs text-gray-400">View historical alarms and trends</p>
        </div>
        <button className="flex items-center gap-2 text-sm text-cyan-400 hover:text-cyan-300">
          View History
          <ChevronDown className="w-4 h-4 -rotate-90" />
        </button>
      </div>
    </div>
  )
}
