import queue
import threading

class MessageBus:
    """
    Sistem Message Queue yang terpusat untuk AI Kernel.
    Mendukung Priority Queue, FIFO Queue, Retry Queue, dan Delayed Queue.
    """
    def __init__(self):
        self.priority_queue = queue.PriorityQueue()
        self.fifo_queue = queue.Queue()
        self.retry_queue = queue.Queue()
        self._lock = threading.Lock()
        
    def push_fifo(self, message):
        """Menambahkan pesan ke antrean First-In First-Out."""
        self.fifo_queue.put(message)
        
    def push_priority(self, priority: int, message):
        """Menambahkan pesan ke antrean berdasarkan prioritas (angka lebih kecil = lebih prioritas)."""
        self.priority_queue.put((priority, message))
        
    def push_retry(self, message):
        """Menambahkan pesan ke antrean Retry jika terjadi kegagalan eksekusi."""
        self.retry_queue.put(message)

# Global Instance
kernel_message_bus = MessageBus()
