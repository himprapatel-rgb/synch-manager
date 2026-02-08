import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { 
  Bell, 
  AlertTriangle, 
  CheckCircle, 
  Info, 
  XCircle, 
  X, 
  Settings, 
  Filter,
  Trash2,
  CheckCheck,
  Clock
} from 'lucide-react'

const NOTIFICATION_TYPES = {
  alarm: { icon: AlertTriangle, color: 'text-red-500', bg: 'bg-red-500/10' },
  warning: { icon: AlertTriangle, color: 'text-yellow-500', bg: 'bg-yellow-500/10' },
  success: { icon: CheckCircle, color: 'text-green-500', bg: 'bg-green-500/10' },
  info: { icon: Info, color: 'text-blue-500', bg: 'bg-blue-500/10' },
  error: { icon: XCircle, color: 'text-red-500', bg: 'bg-red-500/10' }
}

const NotificationCenter = ({ isOpen, onClose }) => {
  const [notifications, setNotifications] = useState([])
  const [filter, setFilter] = useState('all')
  const [unreadCount, setUnreadCount] = useState(0)

  // Mock notifications - in production would come from WebSocket/API
  useEffect(() => {
    const mockNotifications = [
      {
        id: 1,
        type: 'alarm',
        title: 'Critical Alarm',
        message: 'PTP sync lost on node-03',
        timestamp: new Date(Date.now() - 5 * 60000),
        read: false,
        device: 'TP4100-03',
        severity: 'critical'
      },
      {
        id: 2,
        type: 'warning',
        title: 'Clock Drift Warning',
        message: 'Clock offset exceeding threshold on node-05',
        timestamp: new Date(Date.now() - 15 * 60000),
        read: false,
        device: 'TP5000-05',
        severity: 'major'
      },
      {
        id: 3,
        type: 'success',
        title: 'Sync Restored',
        message: 'PTP synchronization restored on node-01',
        timestamp: new Date(Date.now() - 30 * 60000),
        read: true,
        device: 'GM-01',
        severity: 'cleared'
      },
      {
        id: 4,
        type: 'info',
        title: 'Firmware Update Available',
        message: 'New firmware v2.5.1 available for TimeProvider 4100',
        timestamp: new Date(Date.now() - 60 * 60000),
        read: true,
        device: 'System',
        severity: 'info'
      },
      {
        id: 5,
        type: 'alarm',
        title: 'GNSS Signal Lost',
        message: 'GNSS receiver signal degraded on node-02',
        timestamp: new Date(Date.now() - 2 * 60000),
        read: false,
        device: 'TP4100-02',
        severity: 'critical'
      }
    ]
    setNotifications(mockNotifications)
    setUnreadCount(mockNotifications.filter(n => !n.read).length)
  }, [])

  const markAsRead = (id) => {
    setNotifications(prev => prev.map(n => 
      n.id === id ? { ...n, read: true } : n
    ))
    setUnreadCount(prev => Math.max(0, prev - 1))
  }

  const markAllAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })))
    setUnreadCount(0)
  }

  const deleteNotification = (id) => {
    const notification = notifications.find(n => n.id === id)
    if (notification && !notification.read) {
      setUnreadCount(prev => Math.max(0, prev - 1))
    }
    setNotifications(prev => prev.filter(n => n.id !== id))
  }

  const clearAll = () => {
    setNotifications([])
    setUnreadCount(0)
  }

  const filteredNotifications = notifications.filter(n => {
    if (filter === 'all') return true
    if (filter === 'unread') return !n.read
    return n.type === filter
  })

  const formatTime = (date) => {
    const now = new Date()
    const diff = now - date
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)

    if (minutes < 1) return 'Just now'
    if (minutes < 60) return `${minutes}m ago`
    if (hours < 24) return `${hours}h ago`
    return `${days}d ago`
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="relative w-full max-w-md bg-gray-900 border-l border-gray-700 shadow-xl">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <div className="flex items-center gap-2">
            <Bell className="w-5 h-5 text-cyan-400" />
            <h2 className="text-lg font-semibold text-white">Notifications</h2>
            {unreadCount > 0 && (
              <Badge variant="destructive" className="ml-2">
                {unreadCount} new
              </Badge>
            )}
          </div>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="w-5 h-5" />
          </Button>
        </div>

        {/* Filters */}
        <div className="flex items-center gap-2 p-3 border-b border-gray-700 overflow-x-auto">
          {['all', 'unread', 'alarm', 'warning', 'success', 'info'].map((f) => (
            <Button
              key={f}
              variant={filter === f ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter(f)}
              className="capitalize whitespace-nowrap"
            >
              {f}
            </Button>
          ))}
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between px-4 py-2 border-b border-gray-700">
          <Button variant="ghost" size="sm" onClick={markAllAsRead} disabled={unreadCount === 0}>
            <CheckCheck className="w-4 h-4 mr-2" />
            Mark all read
          </Button>
          <Button variant="ghost" size="sm" onClick={clearAll} disabled={notifications.length === 0}>
            <Trash2 className="w-4 h-4 mr-2" />
            Clear all
          </Button>
        </div>

        {/* Notifications List */}
        <ScrollArea className="h-[calc(100vh-220px)]">
          {filteredNotifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-gray-500">
              <Bell className="w-12 h-12 mb-4 opacity-50" />
              <p>No notifications</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-800">
              {filteredNotifications.map((notification) => {
                const typeConfig = NOTIFICATION_TYPES[notification.type]
                const Icon = typeConfig.icon
                return (
                  <div
                    key={notification.id}
                    className={`p-4 hover:bg-gray-800/50 cursor-pointer transition-colors ${
                      !notification.read ? 'bg-gray-800/30' : ''
                    }`}
                    onClick={() => markAsRead(notification.id)}
                  >
                    <div className="flex gap-3">
                      <div className={`p-2 rounded-lg ${typeConfig.bg}`}>
                        <Icon className={`w-5 h-5 ${typeConfig.color}`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <p className={`font-medium ${!notification.read ? 'text-white' : 'text-gray-300'}`}>
                              {notification.title}
                            </p>
                            <p className="text-sm text-gray-400 mt-0.5">
                              {notification.message}
                            </p>
                          </div>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="shrink-0 h-6 w-6"
                            onClick={(e) => {
                              e.stopPropagation()
                              deleteNotification(notification.id)
                            }}
                          >
                            <X className="w-3 h-3" />
                          </Button>
                        </div>
                        <div className="flex items-center gap-2 mt-2">
                          <Badge variant="outline" className="text-xs">
                            {notification.device}
                          </Badge>
                          <span className="flex items-center text-xs text-gray-500">
                            <Clock className="w-3 h-3 mr-1" />
                            {formatTime(notification.timestamp)}
                          </span>
                          {!notification.read && (
                            <span className="w-2 h-2 bg-cyan-400 rounded-full" />
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </ScrollArea>
      </div>
    </div>
  )
}

export default NotificationCenter
