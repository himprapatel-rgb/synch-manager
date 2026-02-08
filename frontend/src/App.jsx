import { Routes, Route, NavLink } from 'react-router-dom'
import { useState } from 'react'
import { LayoutDashboard, Server, AlertTriangle, BarChart3, Settings, Shield, Clock, Satellite, Menu, X } from 'lucide-react'

// Pages
import Dashboard from './pages/Dashboard'
import Inventory from './pages/Inventory'
import Alarms from './pages/Alarms'
import Performance from './pages/Performance'
import Configuration from './pages/Configuration'
import Security from './pages/Security'
import WarMode from './pages/WarMode'
import GNSSResilience from './pages/GNSSResilience'
import NetworkElementDetail from './pages/NetworkElementDetail'

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Inventory', href: '/inventory', icon: Server },
  { name: 'Alarms', href: '/alarms', icon: AlertTriangle },
  { name: 'Performance', href: '/performance', icon: BarChart3 },
  { name: 'Configuration', href: '/configuration', icon: Settings },
  { name: 'Security', href: '/security', icon: Shield },
  { name: 'War Mode', href: '/war-mode', icon: Clock },
  { name: 'GNSS Resilience', href: '/gnss', icon: Satellite },
]

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Mobile sidebar */}
      <div className={`fixed inset-0 z-50 lg:hidden ${sidebarOpen ? '' : 'hidden'}`}>
        <div className="fixed inset-0 bg-gray-900/80" onClick={() => setSidebarOpen(false)} />
        <div className="fixed inset-y-0 left-0 w-64 bg-gray-800 p-4">
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-xl font-bold text-cyan-400">Synch-Manager</h1>
            <button onClick={() => setSidebarOpen(false)}><X className="w-6 h-6 text-gray-400" /></button>
          </div>
          <nav className="space-y-1">
            {navigation.map((item) => (
              <NavLink key={item.name} to={item.href} onClick={() => setSidebarOpen(false)}
                className={({ isActive }) => `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors
                  ${isActive ? 'bg-cyan-500/20 text-cyan-400' : 'text-gray-400 hover:bg-gray-700 hover:text-white'}`}>
                <item.icon className="w-5 h-5" />{item.name}
              </NavLink>
            ))}
          </nav>
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-col flex-1 bg-gray-800 border-r border-gray-700">
          <div className="flex items-center h-16 px-4 border-b border-gray-700">
            <h1 className="text-xl font-bold text-cyan-400">Synch-Manager</h1>
          </div>
          <nav className="flex-1 p-4 space-y-1">
            {navigation.map((item) => (
              <NavLink key={item.name} to={item.href}
                className={({ isActive }) => `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors
                  ${isActive ? 'bg-cyan-500/20 text-cyan-400' : 'text-gray-400 hover:bg-gray-700 hover:text-white'}`}>
                <item.icon className="w-5 h-5" />{item.name}
              </NavLink>
            ))}
          </nav>
          <div className="p-4 border-t border-gray-700">
            <div className="text-xs text-gray-500">v1.0.0 | Single Pane of Glass</div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        <header className="sticky top-0 z-40 flex items-center h-16 px-4 bg-gray-800 border-b border-gray-700 lg:px-6">
          <button className="lg:hidden" onClick={() => setSidebarOpen(true)}>
            <Menu className="w-6 h-6 text-gray-400" />
          </button>
          <div className="flex-1" />
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center px-2 py-1 text-xs font-medium text-green-400 bg-green-400/10 rounded-full">
              <span className="w-2 h-2 mr-1 bg-green-400 rounded-full animate-pulse" />System Online
            </span>
          </div>
        </header>

        <main className="p-4 lg:p-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/inventory" element={<Inventory />} />
            <Route path="/alarms" element={<Alarms />} />
            <Route path="/performance" element={<Performance />} />
            <Route path="/configuration" element={<Configuration />} />
            <Route path="/security" element={<Security />} />
              <Route path="/inventory/:id" element={<NetworkElementDetail />} />
            <Route path="/war-mode" element={<WarMode />} />
            <Route path="/gnss" element={<GNSSResilience />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}
