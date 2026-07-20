from models.router import model_router
import config
from plugins.agents.base import BaseAgent
from utils.logger import log_warning

class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Planner",
            model_provider="Groq",
            model_name=config.GROQ_MODEL,
            default_reason="Groq (llama-3.3-70b-versatile) sangat cepat dan handal untuk penalaran logis, pembuatan rencana kerja (roadmap), pemecahan masalah (task decomposition), dan alokasi tugas."
        )

    def get_selection_reason(self, task_type: str = "") -> str:
        return self.default_reason

    def run(self, context: dict, user_prompt: str, mock: bool = False) -> str:
        system_prompt = (
            "Anda adalah Planner Agent di Project Nexus.\n"
            "Tugas Anda adalah memecah permintaan pengguna menjadi tugas-tugas terstruktur, "
            "membuat roadmap eksekusi, dan mendistribusikan sub-pekerjaan untuk agen berikutnya.\n"
            "Gunakan format Markdown yang rapi dan terperinci. Fokus pada modularitas dan kejelasan."
        ) + self.get_constitution()
        
        prompt = f"Permintaan Pengguna:\n{user_prompt}"
        
        # Use ModelRouter
        return model_router.complete(
            prompt=prompt,
            system_prompt=system_prompt,
            provider=self.model_provider,
            model=self.model_name,
            temperature=0.2,
            mock=mock
        )

    def _run_mock(self, user_prompt: str) -> str:
        return f"""# Nexus Planner Roadmap & Tasks

Telah dibuat rencana kerja untuk menyelesaikan tugas: **"{user_prompt}"**

## 1. Roadmap Eksekusi

```mermaid
graph TD
    A[User Request] --> B[Planner: Tugas & Roadmap]
    B --> C[Research: Studi Literatur & Teori]
    C --> D[Developer: Implementasi & Kode]
    D --> E[Reviewer: Evaluasi & Validasi]
    E --> F[Output Final]
```

*   **Fase 1: Research (Kimi)** - Menganalisis landasan teori, mencari referensi best practices, dan merumuskan batasan masalah.
*   **Fase 2: Developer (Groq)** - Menulis kode Python, mendesain API yang bersih, dan mengimplementasikan algoritma.
*   **Fase 3: Reviewer (Kimi)** - Melakukan pengujian logis, meninjau kerentanan keamanan, serta memberikan umpan balik optimasi.

## 2. Rincian Pembagian Tugas (Task List)

*   **[RESEARCH-01]** Menganalisis parameter desain, kompleksitas waktu, dan algoritma yang paling efisien untuk "{user_prompt}".
*   **[DEV-01]** Menulis kode Python modular dengan penanganan error yang kuat dan docstring lengkap.
*   **[DEV-02]** Menyusun modul pengujian (unit testing) untuk memverifikasi fungsionalitas utama.
*   **[REVIEW-01]** Melakukan tinjauan kode terhadap standard PEP 8, efisiensi memori, dan keandalan arsitektur.
"""
