from model.router import model_router
import config
from agents.base import BaseAgent
from utils.logger import log_warning

class ReviewerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Reviewer",
            model_provider="Kimi",
            model_name=config.KIMI_MODEL,
            default_reason="Kimi (kimi-k2) memiliki jendela konteks besar dan kemampuan analitis mendalam, sehingga sangat unggul dalam mengevaluasi hasil kerja, menemukan inkonsistensi logis, memberikan kritik arsitektur, dan memvalidasi kebenaran logika kode."
        )

    def get_selection_reason(self, task_type: str = "") -> str:
        return self.default_reason

    def run(self, context: dict, user_prompt: str, mock: bool = False) -> str:
        developer_output = context.get("Developer", "")
        
        system_prompt = (
            "Anda adalah Reviewer Agent di Project Nexus.\n"
            "Tugas Anda adalah mengevaluasi kode sumber dan solusi dari Developer Agent secara kritis.\n"
            "Cari inkonsistensi, evaluasi logika, berikan kritik konstruktif, serta jelaskan trade-off dari desain yang dipilih.\n"
            "Berikan status evaluasi akhir berupa [PASS] atau [FAIL] disertai alasan kuat."
        ) + self.get_constitution()
        
        user_content = (
            f"Tujuan Utama: {user_prompt}\n\n"
            f"Kode/Solusi Developer:\n{developer_output}"
        )
        
        # Use ModelRouter
        return model_router.complete(
            prompt=user_content,
            system_prompt=system_prompt,
            provider=self.model_provider,
            model=self.model_name,
            temperature=0.3,
            mock=mock
        )

    def _run_mock(self, user_prompt: str, developer_output: str) -> str:
        return f"""# Nexus Reviewer Evaluation Report

Telah dilakukan audit teknis terhadap kode solusi untuk: **"{user_prompt}"**

## 1. Analisis Kritis & Kebenaran Logika

*   **Thread Safety**: Mekanisme sinkronisasi menggunakan `threading.Lock` di kelas `ThreadSafeKeyValueStore` dinilai benar dan aman. Tindakan lock-acquisition menggunakan statement `with self._lock` mencegah terjadinya deadlock jika terjadi error di tengah eksekusi.
*   **Completeness**: Implementasi mencakup operasi CRUD dasar (Create, Read, Delete).
*   **Logging**: Logger diimplementasikan secara modular namun belum mendukung rotasi log (log rotation) atau kustomisasi level eksternal.

## 2. Desain Trade-offs & Kritik Arsitektur

*   **Penyimpanan In-Memory**: Semua data disimpan di RAM (`Dict[str, Any]`). Ini memiliki kecepatan tinggi (O(1) access time), namun tidak persisten. Jika aplikasi crash, semua data akan hilang.
    *   *Trade-off*: Mengorbankan ketahanan data (durability) demi kecepatan akses (speed).
*   **Global Lock Bottleneck**: Menggunakan satu lock tunggal memblokir operasi pembacaan konkuren. Pada skenario read-heavy, performa akan melambat secara signifikan.
    *   *Trade-off*: Kesederhanaan implementasi (safety) mengorbankan skalabilitas konkurensi (throughput).

## 3. Status Evaluasi

**[PASS]**

Kode diimplementasikan dengan sangat baik, rapi, dan modular. Solusi ini layak digunakan sebagai basis dasar atau *Proof of Concept* (PoC).

### Saran Perbaikan (Refactoring):
1.  Gunakan `threading.RLock` jika metode internal perlu memanggil satu sama lain tanpa memicu deadlock diri sendiri.
2.  Tambahkan opsi penyimpanan persisten (misal SQLite atau berkas JSON lokal) di iterasi berikutnya.
"""
