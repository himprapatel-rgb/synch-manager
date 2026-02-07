import { useState, useEffect, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { 
  MapPin, 
  ZoomIn, 
  ZoomOut, 
  Maximize2,
  RefreshCw,
  Layers,
  Filter
} from 'lucide-react'

// Status colors for map markers
const STATUS_COLORS = {
  managed: '#22c55e',
  unmanaged: '#6b7280',
  unavailable: '#ef4444',
  critical: '#dc2626',
  major: '#f97316',
  minor: '#eab308',
  normal: '#22c55e',
}

// Simple world map SVG path (simplified)
const WORLD_MAP_PATH = `M0,100 L50,80 L100,90 L150,70 L200,85 L250,75 L300,80 L350,70 
L400,75 L450,65 L500,80 L550,70 L600,85 L650,75 L700,80 L750,70 L800,90 
L800,300 L0,300 Z`

// Device marker component
function DeviceMarker({ device, x, y, onClick, isSelected }) {
  const statusColor = STATUS_COLORS[device.status] || STATUS_COLORS.normal
  
  return (
    <g 
      transform={`translate(${x}, ${y})`}
      onClick={() => onClick(device)}
      style={{ cursor: 'pointer' }}
    >
      {/* Pulse animation for critical/major */}
      {(device.status === 'critical' || device.status === 'major') && (
        <circle
          r="20"
          fill={statusColor}
          opacity="0.3"
          className="animate-ping"
        />
      )}
      
      {/* Main marker */}
      <circle
        r="12"
        fill={statusColor}
        stroke={isSelected ? '#fff' : 'transparent'}
        strokeWidth="3"
        className="transition-all duration-200 hover:scale-110"
      />
      
      {/* Inner dot */}
      <circle r="4" fill="#fff" />
      
      {/* Label */}
      <text
        y="25"
        textAnchor="middle"
        fill="#fff"
        fontSize="10"
        fontWeight="500"
      >
        {device.name}
      </text>
      
      {/* Alarm badge */}
      {device.alarmCount > 0 && (
        <g transform="translate(8, -8)">
          <circle r="8" fill="#ef4444" />
          <text
            textAnchor="middle"
            dominantBaseline="middle"
            fill="#fff"
            fontSize="8"
            fontWeight="bold"
          >
            {device.alarmCount}
          </text>
        </g>
      )}
    </g>
  )
}

// Connection line between devices
function ConnectionLine({ from, to, status }) {
  const color = status === 'active' ? '#22c55e' : '#6b7280'
  
  return (
    <line
      x1={from.x}
      y1={from.y}
      x2={to.x}
      y2={to.y}
      stroke={color}
      strokeWidth="2"
      strokeDasharray={status === 'active' ? '0' : '5,5'}
      opacity="0.6"
    />
  )
}

export default function TopologyMap({ onDeviceSelect, height = 500 }) {
  const [zoom, setZoom] = useState(1)
  const [pan, setPan] = useState({ x: 0, y: 0 })
  const [selectedDevice, setSelectedDevice] = useState(null)
  const [showFilters, setShowFilters] = useState(false)
  const [statusFilter, setStatusFilter] = useState('all')
  const svgRef = useRef(null)
  const [isDragging, setIsDragging] = useState(false)
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })

  // Fetch network elements
  const { data: devices, isLoading, refetch } = useQuery({
    queryKey: ['topology-devices'],
    queryFn: async () => {
      const res = await fetch('/api/v1/inventory/network-elements/')
      if (!res.ok) throw new Error('Failed to fetch devices')
      const data = await res.json()
      return data.results || []
    },
    refetchInterval: 30000,
  })

  // Generate positions for devices (in real app, use actual coordinates)
  const getDevicePositions = () => {
    if (!devices) return []
    
    return devices.map((device, index) => {
      // If device has coordinates, use them; otherwise distribute evenly
      const lat = device.latitude || (40 + (index * 10) % 60)
      const lon = device.longitude || (-80 + (index * 30) % 160)
      
      // Convert lat/lon to SVG coordinates
      const x = ((lon + 180) / 360) * 800
      const y = ((90 - lat) / 180) * 400
      
      return {
        ...device,
        x,
        y,
        alarmCount: device.alarm_count || 0,
        status: device.status || 'managed'
      }
    })
  }

  const devicePositions = getDevicePositions()

  // Filter devices
  const filteredDevices = statusFilter === 'all' 
    ? devicePositions 
    : devicePositions.filter(d => d.status === statusFilter)

  const handleDeviceClick = (device) => {
    setSelectedDevice(device.id === selectedDevice ? null : device.id)
    if (onDeviceSelect) {
      onDeviceSelect(device)
    }
  }

  const handleZoomIn = () => setZoom(z => Math.min(z * 1.2, 3))
  const handleZoomOut = () => setZoom(z => Math.max(z / 1.2, 0.5))
  const handleReset = () => {
    setZoom(1)
    setPan({ x: 0, y: 0 })
  }

  // Pan handling
  const handleMouseDown = (e) => {
    if (e.button === 0) {
      setIsDragging(true)
      setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y })
    }
  }

  const handleMouseMove = (e) => {
    if (isDragging) {
      setPan({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      })
    }
  }

  const handleMouseUp = () => setIsDragging(false)

  return (
    <div className="relative bg-gray-900 border border-gray-700 rounded-xl overflow-hidden">
      {/* Header */}
      <div className="absolute top-0 left-0 right-0 z-10 flex items-center justify-between p-3 bg-gradient-to-b from-gray-900 to-transparent">
        <h3 className="text-sm font-medium text-white flex items-center gap-2">
          <MapPin className="w-4 h-4 text-cyan-400" />
          Network Topology
        </h3>
        
        <div className="flex items-center gap-2">
          {/* Filter dropdown */}
          <div className="relative">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
            >
              <Filter className="w-4 h-4" />
            </button>
            
            {showFilters && (
              <div className="absolute right-0 mt-1 w-40 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-20">
                {['all', 'managed', 'unmanaged', 'critical', 'major', 'minor'].map(status => (
                  <button
                    key={status}
                    onClick={() => {
                      setStatusFilter(status)
                      setShowFilters(false)
                    }}
                    className={`w-full px-3 py-2 text-left text-sm ${
                      statusFilter === status ? 'text-cyan-400 bg-gray-700' : 'text-gray-300 hover:bg-gray-700'
                    }`}
                  >
                    {status.charAt(0).toUpperCase() + status.slice(1)}
                  </button>
                ))}
              </div>
            )}
          </div>
          
          <button
            onClick={() => refetch()}
            className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Zoom controls */}
      <div className="absolute left-3 top-1/2 -translate-y-1/2 z-10 flex flex-col gap-1 bg-gray-800/80 rounded-lg p-1">
        <button
          onClick={handleZoomIn}
          className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          onClick={handleZoomOut}
          className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <button
          onClick={handleReset}
          className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
        >
          <Maximize2 className="w-4 h-4" />
        </button>
      </div>

      {/* Map SVG */}
      <svg
        ref={svgRef}
        width="100%"
        height={height}
        viewBox="0 0 800 400"
        className="cursor-move"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        <g transform={`translate(${pan.x}, ${pan.y}) scale(${zoom})`}>
          {/* Background grid */}
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#374151" strokeWidth="0.5" />
            </pattern>
          </defs>
          <rect width="800" height="400" fill="url(#grid)" />
          
          {/* Simplified world outline */}
          <path
            d={WORLD_MAP_PATH}
            fill="#1f2937"
            stroke="#374151"
            strokeWidth="1"
            opacity="0.5"
          />

          {/* Connection lines (example connections) */}
          {filteredDevices.length > 1 && filteredDevices.slice(0, -1).map((device, i) => (
            <ConnectionLine
              key={`conn-${i}`}
              from={{ x: device.x, y: device.y }}
              to={{ x: filteredDevices[i + 1].x, y: filteredDevices[i + 1].y }}
              status="active"
            />
          ))}

          {/* Device markers */}
          {filteredDevices.map((device) => (
            <DeviceMarker
              key={device.id}
              device={device}
              x={device.x}
              y={device.y}
              onClick={handleDeviceClick}
              isSelected={selectedDevice === device.id}
            />
          ))}
        </g>
      </svg>

      {/* Legend */}
      <div className="absolute bottom-3 right-3 bg-gray-800/90 rounded-lg p-3">
        <p className="text-xs font-medium text-gray-400 mb-2">Status</p>
        <div className="space-y-1">
          {Object.entries(STATUS_COLORS).slice(0, 5).map(([status, color]) => (
            <div key={status} className="flex items-center gap-2">
              <span 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: color }}
              />
              <span className="text-xs text-gray-300 capitalize">{status}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Loading overlay */}
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900/80">
          <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
        </div>
      )}

      {/* Device count badge */}
      <div className="absolute bottom-3 left-3 px-3 py-1 bg-gray-800/90 rounded-lg">
        <span className="text-xs text-gray-400">
          {filteredDevices.length} device{filteredDevices.length !== 1 ? 's' : ''}
        </span>
      </div>
    </div>
  )
}
