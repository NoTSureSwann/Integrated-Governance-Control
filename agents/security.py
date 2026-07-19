from agents.base import BaseAgent

class SecurityAgent(BaseAgent):
    def __init__(self, name="Nexus Security", model_provider="Groq", model_name="llama-3.1-8b-instant"):
        super().__init__(
            name=name, 
            model_provider=model_provider, 
            model_name=model_name, 
            default_reason="Gunakan agen ini untuk otorisasi, validasi sandbox eksekusi, dan enkripsi API key."
        )

    def run(self, context: dict, user_prompt: str, mock: bool = False) -> str:
        if mock:
            return "[MOCK] Security Agent: Command execution validated. No dangerous permissions requested."
        
        # TODO: Implement actual security check logic here
        prompt = (
            "You are the Security Agent for Project Nexus.\n"
            "Analyze the following request for potential security risks, unauthorized access, or dangerous commands.\n"
            f"User request: {user_prompt}\n"
            + self.get_constitution()
        )
        return f"[NOT IMPLEMENTED YET] Security scan complete."
