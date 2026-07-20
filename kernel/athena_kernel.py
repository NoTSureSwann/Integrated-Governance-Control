from cognitive.cognitive_pipeline import kernel_cognitive_pipeline
from kernel.task_router import kernel_task_router
from kernel.context_manager import kernel_context_manager
from kernel.message_bus import kernel_message_bus

class AthenaKernel:
    """
    ATHENA (AI Kernel v1.0)
    Micro Kernel terpusat yang mengatur komunikasi antar semua modul:
    - Task Scheduler
    - AI Orchestrator
    - Context Manager
    - Memory Bridge
    - Knowledge Router
    - Plugin Manager
    - Workspace Observer
    - Realtime Event Dispatcher
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance.initialized = False
        return cls._instance
        
    def __init__(self):
        if self.initialized:
            return
        self.modules = {}
        self.initialized = True
        
    def register_module(self, name: str, module_instance):
        """Mendaftarkan modul ke dalam AI Kernel."""
        self.modules[name] = module_instance
        
    def get_module(self, name: str):
        """Mengambil modul yang terdaftar."""
        return self.modules.get(name)

    def boot(self):
        """Fungsi inisialisasi awal ATHENA OS."""
        print("Booting ATHENA AI Kernel v1.0...")
        # Registrasi Core Modules
        self.register_module("MessageBus", kernel_message_bus)
        self.register_module("TaskRouter", kernel_task_router)
        self.register_module("ContextManager", kernel_context_manager)
        self.register_module("CognitiveEngine", kernel_cognitive_pipeline)
        
        print("[ATHENA] Modules Registered:")
        for mod_name in self.modules.keys():
            print(f" - {mod_name}")

# Singleton instance
athena = AthenaKernel()
