class TaskRouter:
    """
    Task Router untuk mendeteksi tipe task dan mendelegasikan ke Agen AI yang sesuai.
    Berdasarkan spesifikasi:
    - coding -> Kimi
    - reasoning -> Llama
    - documentation -> Kimi + Llama
    - architecture -> Llama
    - research -> Llama + Knowledge Engine
    - repository -> Kimi
    - dataset -> Knowledge Engine
    - image -> Vision Module
    """
    def __init__(self):
        pass

    def detect_and_route(self, prompt: str) -> list:
        """
        Mendeteksi tipe tugas (task type) dari prompt pengguna dan mengembalikan rute (daftar agen/modul).
        (Implementasi regex/semantic dasar)
        """
        prompt_lower = prompt.lower()
        routes = []
        
        if any(kw in prompt_lower for kw in ["code", "kode", "script", "fungsi"]):
            routes.append("Developer") # Kimi mapping
            
        if any(kw in prompt_lower for kw in ["reason", "mengapa", "analisis logika", "bagaimana"]):
            routes.append("Planner")   # Llama mapping
            
        if any(kw in prompt_lower for kw in ["arsitektur", "design pattern", "arsitektur sistem"]):
            routes.append("Planner")
            
        if any(kw in prompt_lower for kw in ["riset", "research", "cari tahu", "pelajari"]):
            routes.append("Research")
            
        if any(kw in prompt_lower for kw in ["repo", "github", "git"]):
            routes.append("GitHubAnalyzer")
            
        # Fallback default
        if not routes:
            routes = ["Planner", "Developer", "Executor", "Reviewer"]
            
        return routes

# Global instance
kernel_task_router = TaskRouter()
