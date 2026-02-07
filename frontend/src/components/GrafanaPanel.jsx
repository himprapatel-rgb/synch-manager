import { useState } from 'react'
import { ExternalLink, Maximize2, RefreshCw } from 'lucide-react'

const GRAFANA_URL = import.meta.env.VITE_GRAFANA_URL || 'http://localhost:3000'

export default function GrafanaPanel({ title, panelId, dashboardUid, height = 300, refreshInterval = 30000 }) {
  const [isLoading, setIsLoading] = useState(true)
  const [key, setKey] = useState(0)

  // Build Grafana panel embed URL
  const panelUrl = `${GRAFANA_URL}/d-solo/${dashboardUid}?orgId=1&panelId=${panelId}&theme=dark&kiosk`

  const handleRefresh = () => {
    setKey(prev => prev + 1)
    setIsLoading(true)
  }

  const openInGrafana = () => {
    window.open(`${GRAFANA_URL}/d/${dashboardUid}?orgId=1&viewPanel=${panelId}`, '_blank')
  }

  return (
    <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-700">
        <h3 className="text-sm font-medium text-white">{title}</h3>
        <div className="flex items-center gap-2">
          <button onClick={handleRefresh} className="p-1 text-gray-400 hover:text-white rounded">
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
          <button onClick={openInGrafana} className="p-1 text-gray-400 hover:text-white rounded">
            <ExternalLink className="w-4 h-4" />
          </button>
        </div>
      </div>
      <div className="relative" style={{ height }}>
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-800">
            <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
          </div>
        )}
        <iframe
          key={key}
          src={panelUrl}
          className="w-full h-full border-0"
          onLoad={() => setIsLoading(false)}
          title={title}
        />
      </div>
    </div>
  )
}
