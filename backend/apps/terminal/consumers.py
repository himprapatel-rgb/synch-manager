import json
import asyncio
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
import paramiko
import threading

logger = logging.getLogger(__name__)

class SSHConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for SSH terminal connections.
    Establishes SSH connection to network devices and relays terminal I/O.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ssh_client = None
        self.ssh_channel = None
        self.read_thread = None
        
    async def connect(self):
        """Accept WebSocket connection"""
        await self.accept()
        logger.info(f"WebSocket connected: {self.channel_name}")
        
    async def disconnect(self, close_code):
        """Close SSH connection when WebSocket disconnects"""
        await self.close_ssh()
        logger.info(f"WebSocket disconnected: {self.channel_name}")
        
    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'connect':
                await self.handle_connect(data)
            elif action == 'input':
                await self.handle_input(data)
            elif action == 'resize':
                await self.handle_resize(data)
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))
            
    async def handle_connect(self, data):
        """Establish SSH connection to device"""
        host = data.get('host')
        port = data.get('port', 22)
        username = data.get('username', 'admin')
        password = data.get('password', '')
        
        try:
            # Run SSH connection in thread to avoid blocking
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.connect_ssh,
                host, port, username, password
            )
            
            await self.send(text_data=json.dumps({
                'type': 'connected',
                'message': f'Connected to {host}'
            }))
            
            # Start reading output from SSH
            self.read_thread = threading.Thread(
                target=self.read_ssh_output,
                daemon=True
            )
            self.read_thread.start()
            
        except Exception as e:
            logger.error(f"SSH connection failed: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Connection failed: {str(e)}'
            }))
            
    def connect_ssh(self, host, port, username, password):
        """Create SSH connection (runs in thread)"""
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        self.ssh_client.connect(
            hostname=host,
            port=port,
            username=username,
            password=password,
            timeout=10,
            look_for_keys=False,
            allow_agent=False
        )
        
        # Request interactive shell
        self.ssh_channel = self.ssh_client.invoke_shell()
        self.ssh_channel.settimeout(0.0)
        
    def read_ssh_output(self):
        """Read output from SSH channel and send to WebSocket"""
        try:
            while self.ssh_channel and not self.ssh_channel.closed:
                if self.ssh_channel.recv_ready():
                    output = self.ssh_channel.recv(1024).decode('utf-8', errors='ignore')
                    
                    # Send output to WebSocket
                    asyncio.run_coroutine_threadsafe(
                        self.send(text_data=json.dumps({
                            'type': 'output',
                            'data': output
                        })),
                        asyncio.get_event_loop()
                    )
                    
                asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: threading.Event().wait(0.01)
                )
                
        except Exception as e:
            logger.error(f"Error reading SSH output: {e}")
            
    async def handle_input(self, data):
        """Send user input to SSH channel"""
        if self.ssh_channel and not self.ssh_channel.closed:
            command = data.get('data', '')
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.ssh_channel.send,
                command.encode('utf-8')
            )
            
    async def handle_resize(self, data):
        """Resize SSH terminal"""
        if self.ssh_channel:
            rows = data.get('rows', 24)
            cols = data.get('cols', 80)
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.ssh_channel.resize_pty,
                cols, rows
            )
            
    async def close_ssh(self):
        """Close SSH connection"""
        try:
            if self.ssh_channel:
                self.ssh_channel.close()
                self.ssh_channel = None
                
            if self.ssh_client:
                self.ssh_client.close()
                self.ssh_client = None
                
        except Exception as e:
            logger.error(f"Error closing SSH: {e}")
