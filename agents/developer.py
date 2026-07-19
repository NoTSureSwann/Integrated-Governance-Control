from model.router import model_router
import config
from agents.base import BaseAgent
from utils.logger import log_warning

class DeveloperAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Developer",
            model_provider="Groq",
            model_name=config.GROQ_MODEL,
            default_reason="Groq (llama-3.3-70b-versatile) memiliki kecerdasan logika dan sintaksis pemrograman yang luar biasa, sehingga sangat cocok untuk penulisan kode sumber (coding), pembuatan API, debugging, optimasi, dan refactoring."
        )

    def get_selection_reason(self, task_type: str = "") -> str:
        return self.default_reason

    def run(self, context: dict, user_prompt: str, mock: bool = False) -> str:
        planner_output = context.get("Planner", "")
        research_output = context.get("Research", "")
        
        system_prompt = (
            "Anda adalah Developer Agent di Project Nexus.\n"
            "Tugas Anda adalah menulis kode sumber Python, merancang API, melakukan optimasi, "
            "dan menyusun unit test berdasarkan rencana kerja Planner dan tinjauan teoretis dari Research.\n"
            "Berikan solusi kode yang bersih, terdokumentasi dengan baik, modular, dan siap dijalankan."
        ) + self.get_constitution()
        
        user_content = (
            f"Tujuan Utama: {user_prompt}\n\n"
            f"Rencana Kerja Planner:\n{planner_output}\n\n"
            f"Tinjauan Riset:\n{research_output}"
        )
        
        # Use ModelRouter
        return model_router.complete(
            prompt=user_content,
            system_prompt=system_prompt,
            provider=self.model_provider,
            model=self.model_name,
            temperature=0.2,
            mock=mock
        )

    def _run_mock(self, user_prompt: str, planner_output: str, research_output: str) -> str:
        return f"""# Nexus Developer Implementation Code

Berdasarkan rencana pengembangan untuk target **"{user_prompt}"**, berikut adalah prototipe kode Python yang modular dan terdokumentasi.

```python
# example_solution.py
import logging
import threading
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("NexusSolution")

class ThreadSafeKeyValueStore:
    \"\"\"
    Implementasi Thread-Safe Key-Value Store sederhana untuk mendemonstrasikan
    keandalan multi-threading dengan locking.
    \"\"\"
    def __init__(self) -> None:
        self._store: Dict[str, Any] = {{}}
        self._lock = threading.Lock()
        logger.info("KeyValueStore berhasil diinisialisasi.")

    def set(self, key: str, value: Any) -> None:
        \"\"\"Menyimpan nilai ke dalam store secara thread-safe.\"\"\"
        with self._lock:
            self._store[key] = value
            logger.info(f"Key '{{key}}' berhasil disimpan.")

    def get(self, key: str) -> Optional[Any]:
        \"\"\"Mengambil nilai dari store berdasarkan key.\"\"\"
        with self._lock:
            value = self._store.get(key, None)
            logger.info(f"Pengambilan key '{{key}}': {{'Ditemukan' if value is not None else 'Tidak Ditemukan'}}")
            return value

    def delete(self, key: str) -> bool:
        \"\"\"Menghapus key dari store. Mengembalikan True jika berhasil dihapus.\"\"\"
        with self._lock:
            if key in self._store:
                del self._store[key]
                logger.info(f"Key '{{key}}' berhasil dihapus.")
                return True
            logger.warning(f"Key '{{key}}' gagal dihapus karena tidak ada.")
            return False

# Unit Testing Sederhana
def run_tests():
    store = ThreadSafeKeyValueStore()
    
    # Test Set & Get
    store.set("version", "0.1")
    assert store.get("version") == "0.1", "Gagal melakukan GET pada key 'version'"
    
    # Test Delete
    deleted = store.delete("version")
    assert deleted is True, "Gagal melakukan DELETE pada key 'version'"
    assert store.get("version") is None, "Key 'version' masih ada setelah dihapus"
    
    print("Semua unit test berhasil dijalankan!")

if __name__ == "__main__":
    run_tests()
```

## Cara Menjalankan Kode
1. Salin kode di atas ke dalam berkas `example_solution.py`.
2. Jalankan perintah `python example_solution.py` di terminal Anda.
"""
