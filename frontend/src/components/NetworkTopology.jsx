import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { AlertCircle, Network, RefreshCw, ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';
import './NetworkTopology.css';

const NetworkTopology = () => {
  const [devices, setDevices] = useState([]);
  const [connections, setConnections] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const canvasRef = useRef(null);
  const isDragging = useRef(false);
  const dragStart = useRef({ x: 0, y: 0 });

  useEffect(() => {
    fetchTopologyData();
    const interval = setInterval(fetchTopologyData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchTopologyData = async () => {
    try {
      const response = await fetch('/api/network-topology/');
      const data = await response.json();
      setDevices(data.devices || []);
      setConnections(data.connections || []);
    } catch (error) {
      console.error('Error fetching topology:', error);
    }
  };

  useEffect(() => {
    drawTopology();
  }, [devices, connections, zoom, pan]);

  const drawTopology = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    ctx.clearRect(0, 0, width, height);
    ctx.save();
    ctx.translate(pan.x, pan.y);
    ctx.scale(zoom, zoom);

    // Draw connections
    connections.forEach(conn => {
      const from = devices.find(d => d.id === conn.from);
      const to = devices.find(d => d.id === conn.to);
      
      if (from && to) {
        ctx.beginPath();
        ctx.moveTo(from.x, from.y);
        ctx.lineTo(to.x, to.y);
        ctx.strokeStyle = conn.status === 'active' ? '#22c55e' : '#ef4444';
        ctx.lineWidth = 2;
        ctx.stroke();
        
        // Draw bandwidth label
        const midX = (from.x + to.x) / 2;
        const midY = (from.y + to.y) / 2;
        ctx.fillStyle = '#fff';
        ctx.font = '10px Arial';
        ctx.fillText(conn.bandwidth || '', midX, midY);
      }
    });

    // Draw devices
    devices.forEach(device => {
      const isSelected = selectedDevice?.id === device.id;
      const radius = 30;
      
      ctx.beginPath();
      ctx.arc(device.x, device.y, radius, 0, 2 * Math.PI);
      ctx.fillStyle = device.status === 'online' ? '#3b82f6' : '#94a3b8';
      ctx.fill();
      ctx.strokeStyle = isSelected ? '#fbbf24' : '#1e293b';
      ctx.lineWidth = isSelected ? 3 : 1;
      ctx.stroke();
      
      // Device icon/text
      ctx.fillStyle = '#fff';
      ctx.font = 'bold 12px Arial';
      ctx.textAlign = 'center';
      ctx.fillText(device.type?.substring(0, 3).toUpperCase() || 'DEV', device.x, device.y + 4);
      
      // Device name
      ctx.fillStyle = '#000';
      ctx.font = '11px Arial';
      ctx.fillText(device.name, device.x, device.y + radius + 15);
      
      // Status indicator
      if (device.alarms > 0) {
        ctx.beginPath();
        ctx.arc(device.x + radius - 5, device.y - radius + 5, 8, 0, 2 * Math.PI);
        ctx.fillStyle = '#ef4444';
        ctx.fill();
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 10px Arial';
        ctx.fillText(device.alarms, device.x + radius - 5, device.y - radius + 8);
      }
    });

    ctx.restore();
  };

  const handleCanvasClick = (e) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left - pan.x) / zoom;
    const y = (e.clientY - rect.top - pan.y) / zoom;

    const clicked = devices.find(device => {
      const distance = Math.sqrt(
        Math.pow(device.x - x, 2) + Math.pow(device.y - y, 2)
      );
      return distance <= 30;
    });

    setSelectedDevice(clicked || null);
  };

  const handleMouseDown = (e) => {
    isDragging.current = true;
    dragStart.current = { x: e.clientX - pan.x, y: e.clientY - pan.y };
  };

  const handleMouseMove = (e) => {
    if (isDragging.current) {
      setPan({
        x: e.clientX - dragStart.current.x,
        y: e.clientY - dragStart.current.y
      });
    }
  };

  const handleMouseUp = () => {
    isDragging.current = false;
  };

  const handleZoomIn = () => setZoom(prev => Math.min(prev + 0.2, 3));
  const handleZoomOut = () => setZoom(prev => Math.max(prev - 0.2, 0.5));
  const handleReset = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  return (
    <div className="network-topology-container">
      <Card className="h-full">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Network className="h-5 w-5" />
            Network Topology
          </CardTitle>
          <div className="flex gap-2">
            <Button onClick={handleZoomIn} size="sm" variant="outline">
              <ZoomIn className="h-4 w-4" />
            </Button>
            <Button onClick={handleZoomOut} size="sm" variant="outline">
              <ZoomOut className="h-4 w-4" />
            </Button>
            <Button onClick={handleReset} size="sm" variant="outline">
              <Maximize2 className="h-4 w-4" />
            </Button>
            <Button onClick={fetchTopologyData} size="sm">
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="topology-canvas-wrapper">
            <canvas
              ref={canvasRef}
              width={1200}
              height={700}
              onClick={handleCanvasClick}
              onMouseDown={handleMouseDown}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
              onMouseLeave={handleMouseUp}
              className="topology-canvas"
            />
          </div>
          
          {selectedDevice && (
            <div className="device-info-panel">
              <h3 className="font-bold text-lg mb-2">{selectedDevice.name}</h3>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div><strong>Type:</strong> {selectedDevice.type}</div>
                <div><strong>Status:</strong> 
                  <span className={selectedDevice.status === 'online' ? 'text-green-500' : 'text-red-500'}>
                    {selectedDevice.status}
                  </span>
                </div>
                <div><strong>IP:</strong> {selectedDevice.ip}</div>
                <div><strong>Model:</strong> {selectedDevice.model}</div>
                {selectedDevice.alarms > 0 && (
                  <div className="col-span-2 flex items-center gap-1 text-red-500">
                    <AlertCircle className="h-4 w-4" />
                    {selectedDevice.alarms} Active Alarms
                  </div>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default NetworkTopology;
