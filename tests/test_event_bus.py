import unittest
from services.event_bus import EventBus, NexusEvent

class TestEventBus(unittest.TestCase):
    """
    Test Case untuk memverifikasi fungsionalitas Event Driven Architecture (EventBus).
    """
    def setUp(self):
        self.bus = EventBus()
        # Bersihkan listener sebelum setiap tes
        self.bus._listeners.clear()
        self.received_events = []

    def _sample_callback(self, event: NexusEvent):
        self.received_events.append(event)

    def test_single_event_subscription(self):
        """Menguji registrasi dan penerimaan event bertipe tunggal."""
        self.bus.subscribe("TaskCreated", self._sample_callback)
        
        # Publish event yang didengar
        evt = NexusEvent(event_type="TaskCreated", payload={"task": "Design SIGMA"})
        self.bus.publish(evt)
        
        self.assertEqual(len(self.received_events), 1)
        self.assertEqual(self.received_events[0].event_type, "TaskCreated")
        self.assertEqual(self.received_events[0].payload["task"], "Design SIGMA")
        
        # Publish event yang tidak didengar
        self.bus.publish(NexusEvent(event_type="PluginLoaded"))
        self.assertEqual(len(self.received_events), 1) # Jumlah received event tetap 1

    def test_wildcard_subscription(self):
        """Menguji wildcard '*' yang mendengarkan seluruh jenis event."""
        self.bus.subscribe("*", self._sample_callback)
        
        self.bus.publish(NexusEvent(event_type="TaskStarted"))
        self.bus.publish(NexusEvent(event_type="ModelConnected"))
        self.bus.publish(NexusEvent(event_type="MemoryUpdated"))
        
        self.assertEqual(len(self.received_events), 3)

    def test_unsubscribe(self):
        """Menguji pembatalan langganan event (unsubscribe)."""
        self.bus.subscribe("DatabaseChanged", self._sample_callback)
        
        evt1 = NexusEvent(event_type="DatabaseChanged")
        self.bus.publish(evt1)
        self.assertEqual(len(self.received_events), 1)
        
        # Unsubscribe
        self.bus.unsubscribe("DatabaseChanged", self._sample_callback)
        
        evt2 = NexusEvent(event_type="DatabaseChanged")
        self.bus.publish(evt2)
        self.assertEqual(len(self.received_events), 1) # Tetap 1 karena sudah unsubscribe

if __name__ == "__main__":
    unittest.main()
