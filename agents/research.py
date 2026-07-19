from model.router import model_router
import config
from agents.base import BaseAgent
from utils.logger import log_warning

class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Research",
            model_provider="Kimi",
            model_name=config.KIMI_MODEL,
            default_reason="Kimi (kimi-k2) memiliki Context Window yang panjang, sehingga sangat ideal untuk membaca dokumen penelitian, membandingkan makalah ilmiah, sintesis pengetahuan (knowledge synthesis), dan menyusun landasan teori."
        )

    def get_selection_reason(self, task_type: str = "") -> str:
        return self.default_reason

    def run(self, context: dict, user_prompt: str, mock: bool = False) -> str:
        planner_output = context.get("Planner", "")
        
        system_prompt = (
            "Anda adalah Research Agent di Project Nexus.\n"
            "Tugas Anda adalah menganalisis landasan teori, melakukan tinjauan literatur, "
            "dan menyusun dokumen riset/pengetahuan terperinci berdasarkan rencana kerja dari Planner Agent.\n"
            "Fokus pada fakta ilmiah, sebutkan referensi jika memungkinkan, dan sintesiskan informasi secara mendalam."
        ) + self.get_constitution()
        
        user_content = (
            f"Tujuan Utama: {user_prompt}\n\n"
            f"Rencana Kerja Planner:\n{planner_output}"
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

    def _run_mock(self, user_prompt: str, planner_output: str) -> str:
        return f"""# Nexus Research & Literature Review

Berdasarkan target **"{user_prompt}"** dan arahan dari Planner, berikut adalah rangkuman riset serta landasan teori pendukung.

## 1. Tinjauan Literatur & Konsep Kunci

*   **Modularitas Arsitektur**: Teori *Separation of Concerns* (Parnas, 1972) menekankan bahwa sistem modular meminimalkan efek samping dari perubahan kode. Struktur paket Python dengan modul-modul independen adalah penerapan praktis dari prinsip ini.
*   **State Management**: Untuk mengoordinasikan agen berurutan, State Object (Pattern) diperlukan guna melacak data transisi. State harus bersifat immutable (read-only) bagi agen lain atau ditransfer secara aman lewat orkestrator terpusat.
*   **Optimasi Pengujian**: *Test-Driven Development* (Beck, 2003) menunjukkan bahwa unit testing meningkatkan kualitas desain sistem secara dramatis.

## 2. Rekomendasi Teknis untuk Pengembangan

1.  **Enkapsulasi Logic**: Pastikan kelas `BaseAgent` memiliki kontrak interface yang jelas.
2.  **Robust Error Handling**: Panggil API dengan block `try-except` untuk menangani kegagalan koneksi atau autentikasi secara elegan (dan fallback ke mock data jika diperlukan).
3.  **Reproducibility**: Simpan setiap eksekusi pipeline dalam format Markdown dan JSON untuk audit eksperimen laboratorium AI yang dapat direproduksi.
"""
