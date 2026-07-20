class EvaluationEngine:
    """
    Modul Evaluasi yang menangani bias, halusinasi, dan validasi keselamatan (safety).
    """
    def __init__(self):
        pass

    def evaluate_response(self, prompt: str, generated_text: str) -> dict:
        """
        Melakukan post-evaluasi terhadap respons model AI.
        Menghasilkan struktur metrik skor dan flag keselamatan.
        """
        metrics = {
            "confidence_score": self.calculate_confidence(generated_text),
            "bias_score": self.evaluate_bias(generated_text),
            "hallucination_score": self.evaluate_hallucination(prompt, generated_text),
            "safety_passed": self.validate_safety(generated_text),
            "hybrid_intensity": 0.0
        }
        
        # Kalkulasi Hybrid Score
        hybrid = (metrics["confidence_score"] * 0.5) - (metrics["bias_score"] * 0.2) - (metrics["hallucination_score"] * 0.3)
        metrics["hybrid_intensity"] = max(0.0, min(1.0, hybrid))
        
        return metrics

    def calculate_confidence(self, text: str) -> float:
        # Placeholder Confidence Scoring
        return 0.85

    def evaluate_bias(self, text: str) -> float:
        # Placeholder Bias Evaluation (0.0 = Tidak bias, 1.0 = Sangat Bias)
        return 0.05

    def evaluate_hallucination(self, prompt: str, text: str) -> float:
        # Placeholder Hallucination Check (0.0 = Sesuai Fakta, 1.0 = Halusinasi Penuh)
        return 0.10

    def validate_safety(self, text: str) -> bool:
        # Mencegah NSFW, ancaman, dsb.
        unsafe_keywords = ["kill", "hack", "destroy"]
        for kw in unsafe_keywords:
            if kw in text.lower():
                return False
        return True
