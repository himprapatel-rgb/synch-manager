import React, { useState, useEffect } from 'react';

const ThreatVisualization = () => {
  const [threats, setThreats] = useState([]);
  const [stats, setStats] = useState({
    total: 0,
    jamming: 0,
    spoofing: 0,
    resolved: 0
  });

  useEffect(() => {
    // Fetch threat data from API
    const fetchThreats = async () => {
      try {
        const response = await fetch('/api/security/threats/');
        const data = await response.json();
        setThreats(data);
        
        // Calculate stats
        const jammingCount = data.filter(t => t.threat_type === 'jamming').length;
        const spoofingCount = data.filter(t => t.threat_type === 'spoofing').length;
        const resolvedCount = data.filter(t => t.resolved).length;
        
        setStats({
          total: data.length,
          jamming: jammingCount,
          spoofing: spoofingCount,
          resolved: resolvedCount
        });
      } catch (error) {
        console.error('Failed to fetch threats:', error);
      }
    };

    fetchThreats();
    const interval = setInterval(fetchThreats, 5000); // Refresh every 5s
    return () => clearInterval(interval);
  }, []);

  const getThreatColor = (severity) => {
    switch(severity) {
      case 'critical': return 'bg-red-600';
      case 'high': return 'bg-orange-500';
      case 'medium': return 'bg-yellow-500';
      case 'low': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  };

  const getThreatIcon = (type) => {
    return type === 'jamming' ? '📡' : '🛰️';
  };

  return (
    <div className="threat-visualization p-6 bg-gray-900 text-white rounded-lg">
      <h2 className="text-2xl font-bold mb-6">GNSS Threat Monitor</h2>
      
      {/* Stats Overview */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-800 p-4 rounded-lg">
          <div className="text-3xl font-bold">{stats.total}</div>
          <div className="text-sm text-gray-400">Total Threats</div>
        </div>
        <div className="bg-orange-900 p-4 rounded-lg">
          <div className="text-3xl font-bold">{stats.jamming}</div>
          <div className="text-sm text-gray-400">Jamming Events</div>
        </div>
        <div className="bg-purple-900 p-4 rounded-lg">
          <div className="text-3xl font-bold">{stats.spoofing}</div>
          <div className="text-sm text-gray-400">Spoofing Events</div>
        </div>
        <div className="bg-green-900 p-4 rounded-lg">
          <div className="text-3xl font-bold">{stats.resolved}</div>
          <div className="text-sm text-gray-400">Resolved</div>
        </div>
      </div>

      {/* Threat List */}
      <div className="threat-list space-y-4">
        <h3 className="text-xl font-semibold mb-4">Active Threats</h3>
        {threats.length === 0 ? (
          <div className="bg-green-800 p-4 rounded-lg text-center">
            <span className="text-xl">✓</span> No active threats detected
          </div>
        ) : (
          threats.map((threat) => (
            <div
              key={threat.id}
              className="bg-gray-800 p-4 rounded-lg border-l-4 border-orange-500"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  <span className="text-2xl">{getThreatIcon(threat.threat_type)}</span>
                  <div>
                    <div className="font-semibold text-lg capitalize">
                      {threat.threat_type} Detected
                    </div>
                    <div className="text-sm text-gray-400">
                      Device: {threat.device_id}
                    </div>
                    <div className="text-sm text-gray-400">
                      Location: {threat.latitude?.toFixed(4)}, {threat.longitude?.toFixed(4)}
                    </div>
                    <div className="text-xs text-gray-500 mt-2">
                      {new Date(threat.detected_at).toLocaleString()}
                    </div>
                  </div>
                </div>
                <div className="flex flex-col items-end space-y-2">
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-semibold ${getThreatColor(
                      threat.severity
                    )}`}
                  >
                    {threat.severity?.toUpperCase()}
                  </span>
                  {threat.resolved && (
                    <span className="text-green-400 text-sm">✓ Resolved</span>
                  )}
                </div>
              </div>
              
              {/* Threat Details */}
              <div className="mt-3 grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-400">Signal Strength:</span>
                  <span className="ml-2 font-mono">
                    {threat.signal_strength?.toFixed(1)} dBHz
                  </span>
                </div>
                <div>
                  <span className="text-gray-400">Confidence:</span>
                  <span className="ml-2 font-mono">
                    {(threat.confidence * 100)?.toFixed(0)}%
                  </span>
                </div>
              </div>
              
              {/* Mitigation Status */}
              {threat.mitigation_applied && (
                <div className="mt-3 bg-blue-900 p-2 rounded text-sm">
                  <span className="font-semibold">🛡️ Mitigation Active:</span>
                  <span className="ml-2">{threat.mitigation_type}</span>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Threat Heatmap Placeholder */}
      <div className="mt-8">
        <h3 className="text-xl font-semibold mb-4">Threat Heatmap</h3>
        <div className="bg-gray-800 p-6 rounded-lg h-64 flex items-center justify-center">
          <div className="text-gray-500 text-center">
            <div className="text-4xl mb-2">🗺️</div>
            <div>Geographic threat distribution visualization</div>
            <div className="text-sm mt-2">Integrate with mapping library</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ThreatVisualization;
