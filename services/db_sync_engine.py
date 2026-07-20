import threading
import queue
import time
import json
import os
from services.event_bus import EventBus, NexusEvent
from utils.logger import log_info, log_warning
from adapters.database.db_manager import DatabaseManager

class DatabaseSyncEngine:
    """
    Layer 28: Sinkronisasi Database Asinkron.
    Menangkap event DatabaseChanged lalu merambatkan propagasinya:
    MemoryUpdated -> KnowledgeUpdated -> GUI Updated -> Log Updated -> Backup Queue
    """
    def __init__(self):
        self.sync_queue = queue.Queue()
        self._stop_event = threading.Event()
        self.worker_thread = threading.Thread(target=self._sync_worker, daemon=True)
        self.event_bus = EventBus()

    def start(self):
        self.event_bus.subscribe("DatabaseChanged", self._on_database_changed)
        self.worker_thread.start()
        log_info("DatabaseSyncEngine: Rantai sinkronisasi asinkron berjalan di latar belakang.")

    def stop(self):
        self._stop_event.set()
        if self.worker_thread.is_alive():
            self.sync_queue.put(None) # sinyal bangun untuk mengakhiri thread
            self.worker_thread.join()

    def _on_database_changed(self, event: NexusEvent):
        # Masukkan event ke dalam antrian sinkronisasi agar tidak memblokir thread yang me-request
        self.sync_queue.put(event)

    def _sync_worker(self):
        while not self._stop_event.is_set():
            try:
                event = self.sync_queue.get(timeout=1.0)
                if event is None:
                    continue
                
                table = event.payload.get("table", "unknown")
                
                # 1. Propagasi MemoryUpdated
                self.event_bus.publish(NexusEvent(event_type="MemoryUpdated", payload={"table": table}, agent="SyncEngine", status="SUCCESS"))
                
                # 2. Propagasi KnowledgeUpdated
                self.event_bus.publish(NexusEvent(event_type="KnowledgeUpdated", payload={"table": table}, agent="SyncEngine", status="SUCCESS"))
                
                # 3. Propagasi GUI Updated
                self.event_bus.publish(NexusEvent(event_type="GuiUpdated", payload={"table": table}, agent="SyncEngine", status="SUCCESS"))
                
                # 4. Propagasi Log Updated
                self.event_bus.publish(NexusEvent(event_type="LogUpdated", payload={"table": table}, agent="SyncEngine", status="SUCCESS"))
                
                # 5. Backup Queue
                if table != "all" and table != "unknown":
                    self._backup_database(table)
                
                self.sync_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                log_warning(f"DatabaseSyncEngine: Gagal melakukan propagasi asinkron: {e}")

    def _backup_database(self, table: str):
        """Mengekspor isi tabel yang berubah ke berkas JSON lokal sebagai backup."""
        try:
            os.makedirs("backups", exist_ok=True)
            db = DatabaseManager()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            
            if cursor.description:
                col_names = [desc[0] for desc in cursor.description]
                data = [dict(zip(col_names, row)) for row in rows]
                
                # Simpan dump tabel
                with open(f"backups/{table}_backup.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    
            conn.close()
            
            # Konfirmasi antrian backup selesai
            self.event_bus.publish(NexusEvent(
                event_type="BackupQueueUpdated",
                payload={"table": table, "status": "backed_up_to_json"},
                agent="SyncEngine",
                status="SUCCESS"
            ))
        except Exception as e:
            log_warning(f"DatabaseSyncEngine: Gagal memproses backup tabel {table}: {e}")

# Singleton instansi
nexus_db_sync_engine = DatabaseSyncEngine()
