import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { 
  ChevronRight, 
  ChevronDown, 
  Server, 
  Folder,
  MoreVertical,
  Settings,
  Bell,
  Activity,
  Trash2,
  RefreshCw,
  Terminal,
  FileText,
  Wifi
} from 'lucide-react'

// Status colors matching TimePictra
const STATUS_COLORS = {
  managed: 'bg-green-500',
  unmanaged: 'bg-gray-500',
  unavailable: 'bg-red-500',
  critical: 'bg-red-600',
  major: 'bg-orange-500',
  minor: 'bg-yellow-500',
  warning: 'bg-yellow-400',
  normal: 'bg-green-400',
}

const STATUS_LABELS = {
  managed: 'Managed',
  unmanaged: 'Unmanaged',
  unavailable: 'Unavailable',
  critical: 'Critical',
  major: 'Major',
  minor: 'Minor',
  warning: 'Warning',
  normal: 'Normal',
}

// Context menu component
function ContextMenu({ x, y, device, onClose, onAction }) {
  const menuItems = [
    { icon: Settings, label: 'Configuration', action: 'configure' },
    { icon: Bell, label: 'View Alarms', action: 'alarms' },
    { icon: Activity, label: 'Performance', action: 'performance' },
    { icon: FileText, label: 'NE Details', action: 'details' },
    { icon: Terminal, label: 'Activity Log', action: 'logs' },
    { icon: Wifi, label: 'IP Ping', action: 'ping' },
    { icon: RefreshCw, label: 'Sync Alarms', action: 'sync' },
    { divider: true },
    { icon: Trash2, label: 'Delete NE', action: 'delete', danger: true },
  ]

  return (
    <>
      <div className="fixed inset-0 z-40" onClick={onClose} />
      <div 
        className="fixed z-50 w-48 py-1 bg-gray-800 border border-gray-700 rounded-lg shadow-xl"
        style={{ left: x, top: y }}
      >
        {menuItems.map((item, idx) => (
          item.divider ? (
            <div key={idx} className="my-1 border-t border-gray-700" />
          ) : (
            <button
              key={idx}
              onClick={() => {
                onAction(item.action, device)
                onClose()
              }}
              className={`w-full flex items-center gap-2 px-3 py-2 text-sm text-left transition-colors ${
                item.danger 
                  ? 'text-red-400 hover:bg-red-500/10' 
                  : 'text-gray-300 hover:bg-gray-700'
              }`}
            >
              <item.icon className="w-4 h-4" />
              {item.label}
            </button>
          )
        ))}
      </div>
    </>
  )
}

// Tree node component
function TreeNode({ node, level = 0, onSelect, selectedId, onContextMenu }) {
  const [expanded, setExpanded] = useState(level === 0)
  const hasChildren = node.children && node.children.length > 0
  const isSelected = selectedId === node.id
  
  const getStatusColor = () => {
    if (node.type === 'folder') return null
    return STATUS_COLORS[node.status] || STATUS_COLORS.normal
  }

  return (
    <div>
      <div
        className={`flex items-center gap-1 px-2 py-1.5 cursor-pointer transition-colors ${
          isSelected ? 'bg-cyan-500/20 border-l-2 border-cyan-500' : 'hover:bg-gray-700/50'
        }`}
        style={{ paddingLeft: `${level * 16 + 8}px` }}
        onClick={() => {
          if (hasChildren) setExpanded(!expanded)
          onSelect(node)
        }}
        onContextMenu={(e) => {
          e.preventDefault()
          if (node.type !== 'folder') {
            onContextMenu(e, node)
          }
        }}
      >
        {/* Expand/Collapse icon */}
        <span className="w-4 h-4 flex items-center justify-center">
          {hasChildren && (
            expanded ? (
              <ChevronDown className="w-3 h-3 text-gray-400" />
            ) : (
              <ChevronRight className="w-3 h-3 text-gray-400" />
            )
          )}
        </span>
        
        {/* Status indicator or folder icon */}
        {node.type === 'folder' ? (
          <Folder className="w-4 h-4 text-yellow-500" />
        ) : (
          <div className="flex items-center gap-1">
            <span className={`w-2.5 h-2.5 rounded-full ${getStatusColor()}`} />
            <Server className="w-4 h-4 text-gray-400" />
          </div>
        )}
        
        {/* Node label */}
        <span className={`text-sm truncate ${
          isSelected ? 'text-white font-medium' : 'text-gray-300'
        }`}>
          {node.name}
        </span>
        
        {/* Alarm badge */}
        {node.alarmCount > 0 && (
          <span className={`ml-auto px-1.5 py-0.5 text-xs rounded ${
            node.alarmSeverity === 'critical' ? 'bg-red-500/20 text-red-400' :
            node.alarmSeverity === 'major' ? 'bg-orange-500/20 text-orange-400' :
            'bg-yellow-500/20 text-yellow-400'
          }`}>
            {node.alarmCount}
          </span>
        )}
      </div>
      
      {/* Children */}
      {expanded && hasChildren && (
        <div>
          {node.children.map((child) => (
            <TreeNode
              key={child.id}
              node={child}
              level={level + 1}
              onSelect={onSelect}
              selectedId={selectedId}
              onContextMenu={onContextMenu}
            />
          ))}
        </div>
      )}
    </div>
  )
}

// Status legend component
function StatusLegend() {
  const statuses = [
    { status: 'managed', label: 'Managed' },
    { status: 'unmanaged', label: 'Unmanaged' },
    { status: 'unavailable', label: 'Unavailable' },
    { status: 'critical', label: 'Critical' },
    { status: 'major', label: 'Major' },
    { status: 'minor', label: 'Minor' },
  ]

  return (
    <div className="p-3 border-t border-gray-700">
      <p className="mb-2 text-xs font-medium text-gray-400 uppercase">Legend</p>
      <div className="grid grid-cols-2 gap-2">
        {statuses.map(({ status, label }) => (
          <div key={status} className="flex items-center gap-2">
            <span className={`w-2.5 h-2.5 rounded-full ${STATUS_COLORS[status]}`} />
            <span className="text-xs text-gray-400">{label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default function DeviceTree({ onDeviceSelect, onDeviceAction }) {
  const [selectedId, setSelectedId] = useState(null)
  const [contextMenu, setContextMenu] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')

  // Fetch network elements
  const { data: devices, isLoading, refetch } = useQuery({
    queryKey: ['network-elements-tree'],
    queryFn: async () => {
      const res = await fetch('/api/v1/inventory/network-elements/')
      if (!res.ok) throw new Error('Failed to fetch devices')
      const data = await res.json()
      return data.results || []
    },
    refetchInterval: 30000,
  })

  // Build tree structure
  const buildTree = () => {
    if (!devices || devices.length === 0) {
      return [{
        id: 'root',
        name: 'Root',
        type: 'folder',
        children: []
      }]
    }

    // Group devices by type
    const devicesByType = devices.reduce((acc, device) => {
      const type = device.element_type_display || device.element_type || 'Unknown'
      if (!acc[type]) acc[type] = []
      acc[type].push({
        id: device.id,
        name: device.name,
        type: 'device',
        status: device.status || 'managed',
        ip_address: device.ip_address,
        alarmCount: device.alarm_count || 0,
        alarmSeverity: device.alarm_severity || 'minor',
        ...device
      })
      return acc
    }, {})

    return [{
      id: 'root',
      name: 'Root',
      type: 'folder',
      children: Object.entries(devicesByType).map(([type, devs]) => ({
        id: `type-${type}`,
        name: type,
        type: 'folder',
        children: devs
      }))
    }]
  }

  const treeData = buildTree()

  const handleSelect = (node) => {
    setSelectedId(node.id)
    if (node.type !== 'folder' && onDeviceSelect) {
      onDeviceSelect(node)
    }
  }

  const handleContextMenu = (e, device) => {
    setContextMenu({
      x: e.clientX,
      y: e.clientY,
      device
    })
  }

  const handleAction = (action, device) => {
    if (onDeviceAction) {
      onDeviceAction(action, device)
    }
  }

  return (
    <div className="flex flex-col h-full bg-gray-800 border-r border-gray-700">
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-gray-700">
        <h3 className="text-sm font-medium text-white">Network Devices</h3>
        <div className="flex items-center gap-1">
          <button 
            onClick={() => refetch()}
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
            title="Refresh"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button 
            className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
            title="Add Device"
          >
            <MoreVertical className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="p-2 border-b border-gray-700">
        <input
          type="text"
          placeholder="Search devices..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full px-3 py-1.5 text-sm bg-gray-900 border border-gray-700 rounded text-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-cyan-500"
        />
      </div>

      {/* Tree */}
      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="flex items-center justify-center h-32">
            <RefreshCw className="w-5 h-5 text-gray-400 animate-spin" />
          </div>
        ) : (
          treeData.map((node) => (
            <TreeNode
              key={node.id}
              node={node}
              onSelect={handleSelect}
              selectedId={selectedId}
              onContextMenu={handleContextMenu}
            />
          ))
        )}
      </div>

      {/* Legend */}
      <StatusLegend />

      {/* Context Menu */}
      {contextMenu && (
        <ContextMenu
          x={contextMenu.x}
          y={contextMenu.y}
          device={contextMenu.device}
          onClose={() => setContextMenu(null)}
          onAction={handleAction}
        />
      )}
    </div>
  )
}
