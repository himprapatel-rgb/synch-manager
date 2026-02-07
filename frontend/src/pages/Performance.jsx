import GrafanaPanel from '../components/GrafanaPanel'

export default function Performance() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Performance Monitoring</h1>
        <p className="text-gray-400">MTIE, TDEV, and phase metrics with embedded Grafana</p>
      </div>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <GrafanaPanel title="MTIE (Max Time Interval Error)" panelId={1} dashboardUid="performance" height={350} />
        <GrafanaPanel title="TDEV (Time Deviation)" panelId={2} dashboardUid="performance" height={350} />
        <GrafanaPanel title="Phase Offset" panelId={3} dashboardUid="performance" height={350} />
        <GrafanaPanel title="Frequency Drift" panelId={4} dashboardUid="performance" height={350} />
      </div>
    </div>
  )
}
