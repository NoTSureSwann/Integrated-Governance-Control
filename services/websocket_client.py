import asyncio
import json
import websockets
from PySide6.QtCore import QObject, Signal
from services.event_bus import NexusEvent
from utils.logger import log_info, log_warning

class WebSocketClient(QObject):
    """
    WebSocket Client QObject asinkron dengan penanganan koneksi ulang (auto-reconnect)
    untuk mengalirkan data real-time ke halaman visual GUI.
    """
    event_received = Signal(object) # Signal pembawa NexusEvent

    def __init__(self, uri="ws://localhost:8765/ws"):
        super().__init__()
        self.uri = uri
        self._running = True

    async def start(self):
        """Memulai loop koneksi asinkron WebSocket client."""
        log_info(f"Mengkoneksikan WebSocket Client ke {self.uri}...")
        while self._running:
            try:
                async with websockets.connect(self.uri) as websocket:
                    log_info("WebSocket Client berhasil terhubung ke server.")
                    while self._running:
                        message = await websocket.recv()
                        data = json.loads(message)
                        
                        # Bangun kembali objek NexusEvent dari JSON data
                        event = NexusEvent(
                            event_type=data["event_type"],
                            payload=data.get("payload", {}),
                            agent=data.get("agent", "System"),
                            model=data.get("model", "N/A"),
                            status=data.get("status", "INFO"),
                            priority=data.get("priority", "NORMAL"),
                            event_id=data.get("event_id"),
                            timestamp=data.get("timestamp")
                        )
                        
                        # Emit ke GUI thread via Qt Signal
                        self.event_received.emit(event)
            except (websockets.exceptions.ConnectionClosed, ConnectionRefusedError, OSError):
                # Koneksi gagal atau terputus, tunggu 3 detik lalu coba lagi
                await asyncio.sleep(3)
            except Exception as e:
                log_warning(f"WebSocket Client error: {e}")
                await asyncio.sleep(3)

    def stop(self):
        self._running = False

# Instansi klien global untuk langganan real-time di GUI Pages
nexus_ws_client = WebSocketClient()
