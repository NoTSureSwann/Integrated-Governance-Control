from plugins.agents.base import BaseAgent

class SupervisorAgent(BaseAgent):
    def __init__(self, name="Nexus Supervisor", model_provider="Kimi", model_name="moonshot-v1-32k"):
        super().__init__(
            name=name, 
            model_provider=model_provider, 
            model_name=model_name, 
            default_reason="Kimi digunakan sebagai Supervisor karena konteks yang besar (32k+) cocok untuk konsensus dan pengambilan keputusan akhir."
        )

    def run(self, context: dict, user_prompt: str, mock: bool = False) -> str:
        if mock:
            return "[MOCK] Supervisor: Reviewing all agent outputs and reaching consensus. Proceed with execution."
        
        # TODO: Implement actual LLM call here via Model Router
        prompt = (
            "You are the Supervisor Agent for Project Nexus.\n"
            "Review the context from other agents and make a final decision based on consensus.\n"
            f"Context: {context}\n"
            f"Original request: {user_prompt}\n"
            + self.get_constitution()
        )
        return f"[NOT IMPLEMENTED YET] Supervisor decision ready."
