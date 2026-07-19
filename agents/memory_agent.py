from agents.base import BaseAgent

class MemoryAgent(BaseAgent):
    def __init__(self, name="Nexus Memory", model_provider="System", model_name="Local-Vector-DB"):
        super().__init__(
            name=name, 
            model_provider=model_provider, 
            model_name=model_name, 
            default_reason="Agen pengelola Working Memory, Long Term Memory, dan Semantic Memory via ChromaDB/FAISS."
        )

    def run(self, context: dict, user_prompt: str, mock: bool = False) -> str:
        if mock:
            return "[MOCK] Memory Agent: Context retrieved from Working Memory."
        
        # TODO: Implement DB query logic here
        return f"[NOT IMPLEMENTED YET] Memory retrieved."
