import importlib
from typing import Dict, Any
from utils.logger import log_info, log_warning

class PluginManager:
    """
    Plugin Engine v1.0
    Mengelola pendaftaran dan pemuatan agen/plugin secara terpusat.
    """
    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.plugins: Dict[str, Any] = {}

    def load_plugins(self):
        """Memuat agen bawaan secara dinamis dari plugins.agents."""
        agent_configs = [
            ("PlannerAgent", "plugins.agents.planner", "PlannerAgent"),
            ("ResearchAgent", "plugins.agents.research", "ResearchAgent"),
            ("DeveloperAgent", "plugins.agents.developer", "DeveloperAgent"),
            ("ExecutorAgent", "plugins.agents.executor", "ExecutorAgent"),
            ("ReviewerAgent", "plugins.agents.reviewer", "ReviewerAgent"),
        ]
        
        for name, module_path, class_name in agent_configs:
            try:
                mod = importlib.import_module(module_path)
                cls = getattr(mod, class_name)
                self.agents[name] = cls()
                log_info(f"[PluginManager] Berhasil memuat agen: {name}")
            except Exception as e:
                log_warning(f"[PluginManager] Gagal memuat agen {name}: {e}")

    def register_agent(self, name: str, agent_instance: Any):
        self.agents[name] = agent_instance

    def get_agent(self, name: str) -> Any:
        return self.agents.get(name)
