import unittest
import queue
import os
import json
import time
from services.event_bus import EventBus, NexusEvent
from services.db_sync_engine import DatabaseSyncEngine
from adapters.database.memory_adapter import MemoryRepositoryAdapter
from adapters.database.db_manager import DatabaseManager

class TestDatabaseSyncEngine(unittest.TestCase):
    def setUp(self):
        self.event_bus = EventBus()
        self.sync_engine = DatabaseSyncEngine()
        
        # Bersihkan tabel uji
        # Bersihkan tabel uji
        db = DatabaseManager()
        self.memory = MemoryRepositoryAdapter()
        self.memory.clear_all_memory()
        
        # Hapus file backup lama jika ada
        if os.path.exists("backups/knowledge_backup.json"):
            os.remove("backups/knowledge_backup.json")
            
    def test_sync_engine_propagation(self):
        # Mulai sinkronisasi background
        self.sync_engine.start()
        
        # Tangkap event menggunakan list
        received_events = []
        def capture_event(event):
            received_events.append(event.event_type)
            
        self.event_bus.subscribe("MemoryUpdated", capture_event)
        self.event_bus.subscribe("KnowledgeUpdated", capture_event)
        self.event_bus.subscribe("GuiUpdated", capture_event)
        self.event_bus.subscribe("LogUpdated", capture_event)
        self.event_bus.subscribe("BackupQueueUpdated", capture_event)
        
        # Simulasikan trigger DatabaseChanged (seharusnya tabel 'knowledge')
        self.memory.save_knowledge("TEST_KEY", "TEST_VALUE")
        
        # Beri waktu sinkronisasi berjalan sebentar
        time.sleep(0.5)
        
        # Hentikan (join)
        self.sync_engine.stop()
        
        # Verifikasi rantai propagasi Event Bus
        self.assertIn("MemoryUpdated", received_events)
        self.assertIn("KnowledgeUpdated", received_events)
        self.assertIn("GuiUpdated", received_events)
        self.assertIn("LogUpdated", received_events)
        self.assertIn("BackupQueueUpdated", received_events)
        
        # Verifikasi backup JSON terbentuk dan berisi data terbaru
        self.assertTrue(os.path.exists("backups/knowledge_backup.json"))
        with open("backups/knowledge_backup.json", "r") as f:
            data = json.load(f)
            self.assertTrue(any(item["key"] == "TEST_KEY" for item in data))

if __name__ == "__main__":
    unittest.main()
