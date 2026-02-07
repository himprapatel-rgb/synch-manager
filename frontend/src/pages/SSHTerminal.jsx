import { useState, useEffect, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Terminal, Monitor, X } from 'lucide-react'

export default function SSHTerminal() {
  const [selectedDevice, setSelectedDevice] = useState(null)
  const [showConnectionModal, setShowConnectionModal] = useState(true)
  const [connectionStatus, setConnectionStatus] = useState('disconnected')
  const [terminalOutput, setTerminalOutput] = useState([])
  const [inputCommand, setInputCommand] = useState('')
  const terminalRef = useRef(null)

  // Fetch devices from API
  const { data: devices = [] } = useQuery({
    queryKey: ['network-elements'],
    queryFn: async () => {
      const res = await fetch('https://synch-manager-production.up.railway.app/api/v1/inventory/network-elements/')
      if (!res.ok) return []
      const data = await res.json()
      return data.results || data
    }
  })

  // Connect to device
  const handleConnect = (device) => {
    setSelectedDevice(device)
    setShowConnectionModal(false)
    setConnectionStatus('connecting')
    
    // Simulate connection (replace with actual WebSocket/SSH connection)
    setTimeout(() => {
      setConnectionStatus('connected')
      setTerminalOutput([
        `Connecting to ${device.name} (${device.ip_address})...`,
        `SSH connection established`,
        ``,
        `Welcome to ${device.ne_type}`,
        `Last login: ${new Date().toLocaleString()}`,
        ``,
        `${device.name}:~$ `
      ])
    }, 1500)
  }

  // Handle command input
  const handleCommandSubmit = (e) => {
    e.preventDefault()
    if (!inputCommand.trim()) return

    // Add command to output
    setTerminalOutput(prev => [
      ...prev,
      inputCommand,
      `Mock response for: ${inputCommand}`,
      ``,
      `${selectedDevice?.name}:~$ `
    ])
    
    setInputCommand('')
    
    // Scroll to bottom
    setTimeout(() => {
      if (terminalRef.current) {
        terminalRef.current.scrollTop = terminalRef.current.scrollHeight
      }
    }, 10)
  }

  // Disconnect
  const handleDisconnect = () => {
    setConnectionStatus('disconnected')
    setSelectedDevice(null)
    setTerminalOutput([])
    setShowConnectionModal(true)
  }

  // Auto-scroll terminal
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight
    }
  }, [terminalOutput])

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <Terminal className="w-6 h-6" />
              SSH Terminal
            </h1>
            <p className="text-gray-400 mt-1">
              {selectedDevice ? (
                <span>Connected to <span className="text-cyan-400">{selectedDevice.name}</span> ({selectedDevice.ip_address})</span>
              ) : (
                'Select a device to connect'
              )}
            </p>
          </div>
          {selectedDevice && (
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${
                  connectionStatus === 'connected' ? 'bg-green-400' :
                  connectionStatus === 'connecting' ? 'bg-yellow-400 animate-pulse' :
                  'bg-red-400'
                }`} />
                <span className="text-sm text-gray-300 capitalize">{connectionStatus}</span>
              </div>
              <button
                onClick={handleDisconnect}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center gap-2"
              >
                <X className="w-4 h-4" />
                Disconnect
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Connection Modal */}
      {showConnectionModal && (
        <div className="flex-1 flex items-center justify-center bg-gray-900 p-6">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-2xl">
            <h2 className="text-xl font-bold text-white mb-4">Select Device to Connect</h2>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {devices.length === 0 ? (
                <div className="text-center py-8 text-gray-400">
                  <Monitor className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p>No devices available</p>
                </div>
              ) : (
                devices.map((device) => (
                  <button
                    key={device.id}
                    onClick={() => handleConnect(device)}
                    className="w-full p-4 bg-gray-700 hover:bg-gray-600 rounded-lg text-left transition-colors flex items-center justify-between"
                  >
                    <div>
                      <div className="text-white font-medium">{device.name}</div>
                      <div className="text-sm text-gray-400">{device.ip_address} • {device.ne_type}</div>
                    </div>
                    <Terminal className="w-5 h-5 text-cyan-400" />
                  </button>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* Terminal Window */}
      {!showConnectionModal && selectedDevice && (
        <div className="flex-1 flex flex-col bg-black">
          {/* Terminal Output */}
          <div
            ref={terminalRef}
            className="flex-1 overflow-y-auto p-4 font-mono text-sm text-green-400"
            style={{ backgroundColor: '#000' }}
          >
            {terminalOutput.map((line, index) => (
              <div key={index} className="whitespace-pre-wrap">{line}</div>
            ))}
            {connectionStatus === 'connecting' && (
              <div className="text-yellow-400">Connecting... Please wait</div>
            )}
          </div>

          {/* Command Input */}
          {connectionStatus === 'connected' && (
            <div className="bg-gray-900 border-t border-gray-700 p-4">
              <form onSubmit={handleCommandSubmit} className="flex gap-2">
                <span className="text-green-400 font-mono">{selectedDevice.name}:~$</span>
                <input
                  type="text"
                  value={inputCommand}
                  onChange={(e) => setInputCommand(e.target.value)}
                  className="flex-1 bg-transparent text-green-400 font-mono outline-none"
                  placeholder="Type command and press Enter..."
                  autoFocus
                />
              </form>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
