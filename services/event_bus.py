import datetime
import uuid
import threading
from dataclasses import dataclass, field
from PySide6.QtCore import QObject, Signal
from core.ports.event_bus_port import IEventBus

@dataclass
class NexusEvent:
    """
    Model data standar untuk seluruh Event dalam ekosistem Project Nexus.
    """
    event_type: str  # e.g., TaskCreated, TaskStarted, AgentThinking, etc.
    payload: dict = field(default_factory=dict)
    agent: str = "System"
    model: str = "N/A"
    status: str = "INFO"
    priority: str = "NORMAL"
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.datetime.now().isoformat())


class EventBus(IEventBus):
    """
    Thread-safe Singleton Event Bus untuk komunikasi dekapel (decoupled) antar modul.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls, *args, **kwargs)
                cls._instance._listeners = {}
                cls._instance._lock = threading.Lock()
        return cls._instance

    def subscribe(self, event_type: str, callback):
        """Mendaftarkan callback listener untuk tipe event tertentu."""
        with self._lock:
            if event_type not in self._listeners:
                self._listeners[event_type] = []
            if callback not in self._listeners[event_type]:
                self._listeners[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback):
        """Mencabut callback listener dari tipe event tertentu."""
        with self._lock:
            if event_type in self._listeners and callback in self._listeners[event_type]:
                self._listeners[event_type].remove(callback)

    def publish(self, event: NexusEvent):
        """Menerbitkan event ke seluruh subscriber terdaftar secara aman."""
        with self._lock:
            listeners = list(self._listeners.get(event.event_type, []))
            # Tambahkan global listener "*" jika ada
            listeners.extend(self._listeners.get("*", []))
            
        for callback in listeners:
            try:
                callback(event)
            except Exception:
                pass


class QtEventBusBridge(QObject):
    """
    Jembatan khusus Qt (QObject) yang meneruskan event dari standard Python EventBus
    ke dalam Qt Event Loop menggunakan Qt Signals.
    Ini menjamin thread safety saat background thread (AI Agent) mengubah widget UI.
    """
    event_emitted = Signal(object) # Signal yang membawa objek NexusEvent

    def __init__(self):
        super().__init__()
        # Hubungkan bridge ke EventBus global
        EventBus().subscribe("*", self._relay_event)

    def _relay_event(self, event: NexusEvent):
        """Fungsi internal untuk memancarkan sinyal Qt."""
        self.event_emitted.emit(event)

# Instansi global untuk digunakan di seluruh modul GUI
qt_event_bus_bridge = QtEventBusBridge()
