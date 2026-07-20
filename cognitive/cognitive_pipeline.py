import time
from cognitive.preprocessing import PreprocessingModule
from cognitive.feature_engineering import FeatureEngineeringModule
from cognitive.evaluation_engine import EvaluationEngine

class CognitivePipeline:
    """
    Orchestrator utama untuk Hybrid Cognitive Pipeline.
    Mengalirkan teks pengguna melalui Preprocessing -> NLP Features -> (LLM) -> Evaluation.
    """
    def __init__(self):
        self.preprocessor = PreprocessingModule()
        self.feature_extractor = FeatureEngineeringModule()
        self.evaluator = EvaluationEngine()

    def process_input(self, user_input: str) -> dict:
        """
        Fase Pre-Model: Analisis teks sebelum diproses oleh LLM.
        """
        print(f"[CognitiveEngine] Memulai Pre-Processing input: '{user_input[:30]}...'")
        
        # 1. Preprocessing & Normalization
        prep_result = self.preprocessor.run_pipeline(user_input)
        
        # 2. Feature Engineering & Embeddings
        features = self.feature_extractor.extract_features(prep_result["tokens"], prep_result["normalized_text"])
        
        return {
            "original_prompt": user_input,
            "preprocessing": prep_result,
            "features": features
        }

    def process_output(self, original_prompt: str, llm_response: str) -> dict:
        """
        Fase Post-Model: Evaluasi dan validasi output LLM sebelum dikembalikan ke User.
        """
        print("[CognitiveEngine] Mengevaluasi output dari AI Model...")
        
        # 1. Evaluasi Safety, Bias, dan Hallucination
        evaluation = self.evaluator.evaluate_response(original_prompt, llm_response)
        
        if not evaluation["safety_passed"]:
            print("[CognitiveEngine] ⚠️ DITOLAK: Output tidak lulus standar keselamatan!")
            # Fallback jika tidak aman
            llm_response = "Maaf, respons yang dihasilkan tidak memenuhi pedoman keselamatan kami."
            
        return {
            "final_response": llm_response,
            "metrics": evaluation
        }

# Global Instance
kernel_cognitive_pipeline = CognitivePipeline()
