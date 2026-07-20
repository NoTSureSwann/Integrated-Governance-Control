class TaskRouter:
    """
    Task Router Layer v2.0 (Dual Groq Agent Orchestration)
    Mendeteksi intent prompt dan menentukan Model Provider yang paling efisien:
    - Groq1 (Llama-3.3-70b-versatile): Planning, Reasoning, Research, English, Architecture.
    - Groq2 (GPT-OSS-120b): Coding, Code Review, Data Extraction, Deep Analysis.
    """
    def __init__(self):
        pass

    def select_provider(self, prompt: str) -> str:
        """
        Mengembalikan nama provider ("Groq1" atau "Groq2") berdasarkan tipe tugas.
        """
        prompt_lower = prompt.lower()
        
        # Coding & Deep Analysis -> Groq2
        coding_keywords = ["code", "kode", "script", "function", "bug", "refactor", "class", "extract", "json"]
        if any(kw in prompt_lower for kw in coding_keywords):
            return "Groq2"
            
        # Default / Planning & General Reasoning -> Groq1
        return "Groq1"

    def detect_and_route(self, prompt: str) -> dict:
        """
        Mengembalikan rute komprehensif (Agen & Preferred Provider).
        """
        provider = self.select_provider(prompt)
        prompt_lower = prompt.lower()
        agents = []
        
        if any(kw in prompt_lower for kw in ["code", "kode", "script", "fungsi"]):
            agents.append("DeveloperAgent")
            
        if any(kw in prompt_lower for kw in ["reason", "mengapa", "analisis", "bagaimana"]):
            agents.append("PlannerAgent")
            
        if any(kw in prompt_lower for kw in ["riset", "research", "cari tahu"]):
            agents.append("ResearchAgent")
            
        if not agents:
            agents = ["PlannerAgent", "DeveloperAgent", "ReviewerAgent"]
            
        return {
            "provider": provider,
            "agents": agents
        }

# Global instance
kernel_task_router = TaskRouter()

