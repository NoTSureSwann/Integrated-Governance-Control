import unittest
import threading
import time
from services.hook_manager import HookManager, qt_hook_auth_bridge, HookAuthResponse

class TestHookEngine(unittest.TestCase):
    """
    Test Case untuk memverifikasi fungsionalitas lifecycle hooks dan sistem otorisasi.
    """
    def setUp(self):
        self.manager = HookManager()
        # Bersihkan hooks terdaftar sebelum setiap pengujian
        for key in self.manager.hooks:
            self.manager.hooks[key].clear()
            
        self.received_auth_requests = []

    def test_hook_registration_and_execution(self):
        """Memastikan hook berhasil terdaftar dan dieksekusi memodifikasi konteks."""
        def lowercase_prompt_hook(context):
            context["user_prompt"] = context["user_prompt"].lower()
            return context

        self.manager.register_hook("before_task", lowercase_prompt_hook, "Lowercase Prompt")
        
        ctx = {"user_prompt": "HELLO WORLD"}
        result = self.manager.execute_hooks("before_task", ctx)
        
        self.assertEqual(result["user_prompt"], "hello world")

    def test_hook_authorization_flow_approved(self):
        """Memverifikasi alur otorisasi hook saat disetujui (Approved)."""
        # Hook callback yang melipatgandakan nilai data
        def double_value_hook(context):
            context["value"] = context["value"] * 2
            return context

        self.manager.register_hook("before_database", double_value_hook, "Double Value", requires_auth=True)

        # Buat listener mock pada signal otorisasi bridge
        def on_auth_requested(lifecycle, hook_name, event, response_obj):
            self.received_auth_requests.append((lifecycle, hook_name))
            response_obj.approved = True  # Simulasikan klik user menyetujui (Approved)
            event.set()            # Lepas pemblokiran thread

        qt_hook_auth_bridge.auth_requested.connect(on_auth_requested)

        ctx = {"value": 10}
        
        # Eksekusi hook
        result = self.manager.execute_hooks("before_database", ctx)
        
        # Bersihkan koneksi signal
        qt_hook_auth_bridge.auth_requested.disconnect(on_auth_requested)

        self.assertEqual(len(self.received_auth_requests), 1)
        self.assertEqual(self.received_auth_requests[0], ("before_database", "Double Value"))
        self.assertEqual(result["value"], 20)  # Nilai berhasil dikalikan dua karena disetujui

    def test_hook_authorization_flow_denied(self):
        """Memverifikasi alur otorisasi hook saat ditolak (Denied)."""
        def multiply_value_hook(context):
            context["value"] = context["value"] * 3
            return context

        self.manager.register_hook("before_database", multiply_value_hook, "Multiply Value", requires_auth=True)

        def on_auth_requested(lifecycle, hook_name, event, response_obj):
            response_obj.approved = False  # Simulasikan klik user menolak (Denied)
            event.set()

        qt_hook_auth_bridge.auth_requested.connect(on_auth_requested)

        ctx = {"value": 10}
        result = self.manager.execute_hooks("before_database", ctx)
        
        qt_hook_auth_bridge.auth_requested.disconnect(on_auth_requested)

        self.assertEqual(result["value"], 10)  # Nilai tetap 10 karena hook ditolak

if __name__ == "__main__":
    unittest.main()
