import threading
import queue
import time
from services.event_bus import EventBus, NexusEvent
from orchestrator import NexusOrchestrator
import utils.logger as log

class TaskEngine:
    """
    Background Task Engine untuk memproses eksekusi agen (orchestrator)
    secara sekuensial dari sebuah antrean (queue), sehingga tidak memblokir UI.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls, *args, **kwargs)
                cls._instance._task_queue = queue.Queue()
                cls._instance._worker_thread = None
                cls._instance._running = False
                cls._instance._event_bus = EventBus()
        return cls._instance

    def start(self):
        """Memulai background thread untuk memproses antrean."""
        if not self._running:
            self._running = True
            self._worker_thread = threading.Thread(target=self._process_queue, daemon=True)
            self._worker_thread.start()
            log.log_info("TaskEngine background worker started.")

    def stop(self):
        """Menghentikan background thread."""
        self._running = False
        if self._worker_thread:
            # Masukkan dummy task agar loop ter-unblock
            self._task_queue.put(None)
            self._worker_thread.join(timeout=2)
            log.log_info("TaskEngine background worker stopped.")

    def submit_task(self, prompt: str, mock_mode: bool = True):
        """Mengirimkan task baru ke dalam antrean."""
        task_data = {
            "prompt": prompt,
            "mock": mock_mode
        }
        self._task_queue.put(task_data)
        
        # Beritahu UI bahwa task masuk antrean
        queue_size = self._task_queue.qsize()
        self._event_bus.publish(NexusEvent(
            event_type="TaskQueued",
            payload={"message": f"Task added to queue. Position: {queue_size}", "queue_size": queue_size, "prompt": prompt},
            agent="System"
        ))
        log.log_info(f"Task queued. Queue size: {queue_size}")
        
        # Mulai worker jika belum jalan
        if not self._running:
            self.start()

    def _process_queue(self):
        while self._running:
            task_data = self._task_queue.get()
            if task_data is None:
                # Signal stop
                break
            
            prompt = task_data.get("prompt")
            mock_mode = task_data.get("mock", True)
            
            try:
                # Beritahu bahwa task mulai diproses
                self._event_bus.publish(NexusEvent(
                    event_type="TaskStarted",
                    payload={"message": prompt},
                    agent="System"
                ))
                
                # Eksekusi orchestrator
                orchestrator = NexusOrchestrator(mock=mock_mode)
                result = orchestrator.run_pipeline(prompt)
                
                # Beritahu bahwa task selesai
                self._event_bus.publish(NexusEvent(
                    event_type="TaskCompleted",
                    payload={"message": "Pipeline completed successfully.", "result": result},
                    agent="System"
                ))
                
            except Exception as e:
                log.log_error(f"Error executing task: {str(e)}")
                self._event_bus.publish(NexusEvent(
                    event_type="TaskFailed",
                    payload={"message": str(e), "error": str(e)},
                    agent="System"
                ))
                
            finally:
                self._task_queue.task_done()
                
# Global instance
task_engine = TaskEngine()
