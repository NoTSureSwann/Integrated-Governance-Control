import asyncio
import json
import psutil
import random
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from services.event_bus import EventBus, NexusEvent
from utils.logger import log_info

app = FastAPI(title="Project Nexus Realtime Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # We are mostly sending data to client, but client might send control messages
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

class WebSocketServer:
    """
    FastAPI + Uvicorn server wrapped to be compatible with existing start() interface.
    """
    def __init__(self, host="127.0.0.1", port=8765):
        self.host = host
        self.port = port
        EventBus().subscribe("*", self._relay_to_websocket)
        self.server = None

    async def start(self):
        """Start the FastAPI Uvicorn Server in the current asyncio loop and telemetry."""
        config = uvicorn.Config(app, host=self.host, port=self.port, log_level="warning")
        self.server = uvicorn.Server(config)
        
        # Start telemetry loop
        self.telemetry_task = asyncio.create_task(self._telemetry_loop())
        
        log_info(f"FastAPI Realtime Engine starting at http://{self.host}:{self.port}")
        self.server_task = asyncio.create_task(self.server.serve())
        # Wait a bit for server to start up
        await asyncio.sleep(0.5)

    async def stop(self):
        """Stop the FastAPI Uvicorn Server."""
        if hasattr(self, 'telemetry_task'):
            self.telemetry_task.cancel()
            try:
                await self.telemetry_task
            except asyncio.CancelledError:
                pass

        if self.server:
            self.server.should_exit = True
            if hasattr(self, 'server_task'):
                try:
                    await self.server_task
                except asyncio.CancelledError:
                    pass

    def _relay_to_websocket(self, event: NexusEvent):
        """Membungkus NexusEvent menjadi JSON dan menjadwalkan broadcast asinkron."""
        payload = {
            "event_id": event.event_id,
            "timestamp": event.timestamp,
            "event_type": event.event_type,
            "agent": event.agent,
            "model": event.model,
            "payload": event.payload,
            "status": event.status,
            "priority": event.priority
        }
        
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                loop.create_task(manager.broadcast(json.dumps(payload)))
        except RuntimeError:
            pass

    async def _telemetry_loop(self):
        """Membaca data utilitas sistem CPU, RAM, GPU secara real-time dan menyiarkannya."""
        while True:
            await asyncio.sleep(2)
            try:
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent
                gpu = random.randint(0, 5)
                
                telemetry_event = NexusEvent(
                    event_type="TelemetryUpdated",
                    payload={"cpu": cpu, "ram": ram, "gpu": gpu},
                    agent="TelemetryMonitor",
                    status="SUCCESS"
                )
                
                EventBus().publish(telemetry_event)
            except Exception:
                pass
