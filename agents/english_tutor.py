from model.router import model_router
from agents.base import BaseAgent

class EnglishTutorAgent(BaseAgent):
    def __init__(self, name="Nexus English Tutor", model_provider="Groq", model_name="llama-3.1-70b-versatile"):
        super().__init__(
            name=name, 
            model_provider=model_provider, 
            model_name=model_name, 
            default_reason="Gunakan model ini untuk pengajaran Bahasa Inggris, Grammar, Vocabulary, dan percakapan bisnis/akademik."
        )

    def run(self, context: dict, user_prompt: str, mock: bool = False) -> str:
        if mock:
            return self._run_mock(user_prompt)

        system_prompt = (
            "You are an English Tutor focusing on Grammar, Vocabulary, and Pronunciation.\n"
            "Evaluate the user's input. Highlight errors, suggest better words, and explain the rules.\n"
            "At the very end of your response, you MUST include a clean JSON block (without markdown ```json syntax) with this format:\n"
            "{\"level\": \"A1|A2|B1|B2|C1|C2\", \"vocab_score\": 0-100, \"grammar_score\": 0-100, \"writing_score\": 0-100}"
        ) + self.get_constitution()

        return model_router.complete(
            prompt=user_prompt,
            system_prompt=system_prompt,
            provider=self.model_provider,
            model=self.model_name,
            temperature=0.2,
            mock=mock
        )

    def _run_mock(self, user_prompt: str) -> str:
        text = user_prompt.lower()
        
        feedback = f"""# English Writing & Grammar Assessment

- **Teks Input**: "{user_prompt}"
- **Status Analisis**: Offline Simulation (Mock)

## 1. Koreksi Tata Bahasa (Grammar Corrections)
"""
        grammar_score = 75
        vocab_score = 70
        writing_score = 72
        level = "B2"
        
        if "don't" in text and ("he" in text or "she" in text or "it" in text):
            feedback += "- *Kesalahan*: 'He don't / She don't'\n- *Koreksi*: 'He doesn't / She doesn't'\n- *Penjelasan*: Subject ketiga tunggal (He/She/It) menggunakan auxiliary verb 'does not' (doesn't), bukan 'do not' (don't).\n\n"
            grammar_score = 55
            level = "B1"
        else:
            feedback += "Tidak ditemukan kesalahan tata bahasa fatal yang terdeteksi secara otomatis dalam mode offline.\n\n"
            
        feedback += """## 2. Saran Kosakata (Vocabulary Suggestions)
- Cobalah menggunakan kata-kata yang lebih spesifik untuk konteks akademis/teknis. 
  Contoh: ganti 'make' dengan 'develop' atau 'implement' saat berbicara tentang pembuatan kode program.

## 3. Rekomendasi
- Teruskan menulis secara aktif dan saksikan peningkatan skor Anda di Dashboard!
"""
        feedback += f'\n{{"level": "{level}", "vocab_score": {vocab_score}, "grammar_score": {grammar_score}, "writing_score": {writing_score}}}'
        return feedback
