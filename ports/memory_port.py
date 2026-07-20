from typing import Protocol, List, Tuple, Dict, Any

class IMemoryRepository(Protocol):
    """
    Interface untuk Repository Memori (Memory & Database) ekosistem ATHENA/Project Nexus.
    """
    def save_message(self, role: str, content: str) -> None:
        ...
        
    def get_conversation_history(self, limit: int = 100) -> List[Tuple[str, str, str]]:
        ...
        
    def save_knowledge(self, key: str, value: str, source: str = "", category: str = "") -> None:
        ...
        
    def get_all_knowledge(self) -> List[Tuple[str, str, str, str, str]]:
        ...
        
    def save_research(self, task_id: str, summary: str, files_referenced: str = "") -> None:
        ...
        
    def get_all_research(self) -> List[Tuple[str, str, str, str]]:
        ...
        
    def save_long_term(self, concept: str, detail: str, importance_score: int = 5) -> None:
        ...
        
    def get_all_long_term(self) -> List[Tuple[str, str, int, str]]:
        ...
        
    def clear_all_memory(self) -> None:
        ...
        
    def save_english_progress(self, level: str, vocab: int, grammar: int, writing: int) -> None:
        ...
        
    def get_latest_english_progress(self) -> Tuple[str, int, int, int]:
        ...
