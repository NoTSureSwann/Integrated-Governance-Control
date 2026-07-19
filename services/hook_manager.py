import threading
from PySide6.QtCore import QObject, Signal
from utils.logger import log_info, log_warning

class HookAuthResponse:
    """
    Wrapper mutable untuk menampung hasil respon otorisasi pengguna.
    Menggunakan kelas kustom agar referensi objek tetap sama saat dilewatkan via sinyal Qt.
    """
    def __init__(self):
        self.approved = False

class QtHookAuthBridge(QObject):
    """
    Jembatan komunikasi thread-safe untuk meminta persetujuan manual (user authorization)
    dari background thread agen ke GUI thread utama sebelum mengeksekusi modifikasi data.
    """
    auth_requested = Signal(str, str, object, object) # lifecycle, hook_name, threading.Event, HookAuthResponse

class HookRegistration:
    def __init__(self, name: str, func, requires_auth: bool = False):
        self.name = name
        self.func = func
        self.requires_auth = requires_auth

class HookManager:
    """
    Singleton Hook Engine untuk pendaftaran dan pengeksekusian hook daur hidup.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls, *args, **kwargs)
                # Inisialisasi 9 lifecycle hooks yang didukung
                cls._instance.hooks = {
                    "before_task": [],
                    "before_model_call": [],
                    "before_database": [],
                    "before_repository": [],
                    "after_model_call": [],
                    "after_database": [],
                    "after_memory": [],
                    "after_repository": [],
                    "after_output": []
                }
        return cls._instance

    def register_hook(self, lifecycle: str, func, name: str, requires_auth: bool = False):
        """Mendaftarkan plugin/hook baru pada tahap lifecycle tertentu."""
        if lifecycle not in self.hooks:
            log_warning(f"Hook Engine: Tahap lifecycle '{lifecycle}' tidak didukung.")
            return
            
        # Hindari registrasi ganda
        for h in self.hooks[lifecycle]:
            if h.name == name:
                return
                
        hook_reg = HookRegistration(name, func, requires_auth)
        self.hooks[lifecycle].append(hook_reg)
        log_info(f"Hook Engine: Berhasil mendaftarkan hook '{name}' pada '{lifecycle}' (Auth Required: {requires_auth})")

    def execute_hooks(self, lifecycle: str, context: dict) -> dict:
        """
        Mengeksekusi seluruh hook terdaftar pada tahapan lifecycle secara berurutan.
        Mengembalikan context yang mungkin telah termodifikasi.
        """
        if lifecycle not in self.hooks or not self.hooks[lifecycle]:
            return context

        current_context = context.copy()
        
        for hook in self.hooks[lifecycle]:
            if hook.requires_auth:
                # Otorisasi Pengguna Diperlukan (Human First & Preserve User Control)
                event = threading.Event()
                auth_response = HookAuthResponse()
                
                # Pancarkan permintaan otorisasi ke GUI Thread utama
                qt_hook_auth_bridge.auth_requested.emit(lifecycle, hook.name, event, auth_response)
                
                # Blokir thread AI latar belakang secara aman sementara menunggu klik user
                event.wait()
                
                if not auth_response.approved:
                    log_warning(f"Hook Engine: Eksekusi hook '{hook.name}' ditolak oleh pengguna.")
                    continue  # Lewati hook ini jika ditolak
                    
            try:
                # Eksekusi hook callback
                modified_context = hook.func(current_context)
                if isinstance(modified_context, dict):
                    current_context = modified_context
            except Exception as e:
                log_warning(f"Hook Engine: Gagal menjalankan hook '{hook.name}': {e}")
                
        return current_context

# Instansi global untuk diakses di core dan GUI
nexus_hook_manager = HookManager()
qt_hook_auth_bridge = QtHookAuthBridge()
