from adapters.database.db_manager import DatabaseManager, Conversation, Knowledge, Research, LongTerm, EnglishProgress
from utils.logger import log_warning

from ports.memory_port import IMemoryRepository

class MemoryRepositoryAdapter(IMemoryRepository):
    """
    Menyediakan interface terpusat untuk menyimpan dan mengambil data memori
    dari database utama (nexus.db atau PostgreSQL) via SQLAlchemy.
    """
    def __init__(self):
        self.db = DatabaseManager()

    def _emit_db_event(self, event_type: str, table: str, payload: dict):
        """Helper internal untuk memicu event Database/Memory."""
        try:
            from services.event_bus import EventBus, NexusEvent
            sync_payload = {"table": table, "specific_event": event_type, **payload}
            
            EventBus().publish(NexusEvent(
                event_type="DatabaseChanged",
                payload=sync_payload,
                agent="MemoryRepositoryAdapter",
                status="SUCCESS"
            ))
        except Exception:
            pass
        
    # --- CONVERSATION MEMORY ---
    def save_message(self, role: str, content: str):
        """Menyimpan satu baris riwayat pesan (user/agent)."""
        from services.hook_manager import nexus_hook_manager
        
        ctx = nexus_hook_manager.execute_hooks("before_database", {"role": role, "content": content})
        role = ctx.get("role", role)
        content = ctx.get("content", content)
        
        try:
            session = self.db.get_session()
            msg = Conversation(role=role, content=content)
            session.add(msg)
            session.commit()
            session.close()
            
            nexus_hook_manager.execute_hooks("after_database", {"role": role, "content": content, "status": "committed"})
            self._emit_db_event("MemoryUpdated", "conversations", {"role": role, "content": content})
            nexus_hook_manager.execute_hooks("after_memory", {"role": role, "content": content})
        except Exception as e:
            log_warning(f"Memory: Gagal menyimpan pesan: {e}")
            
    def get_conversation_history(self, limit: int = 100) -> list:
        """Mengambil data riwayat percakapan chat terakhir."""
        try:
            session = self.db.get_session()
            results = session.query(Conversation.role, Conversation.content, Conversation.timestamp)\
                             .order_by(Conversation.timestamp.asc())\
                             .limit(limit).all()
            session.close()
            return [(r.role, r.content, r.timestamp) for r in results]
        except Exception as e:
            log_warning(f"Memory: Gagal mengambil riwayat percakapan: {e}")
            return []

    # --- KNOWLEDGE MEMORY ---
    def save_knowledge(self, key: str, value: str, source: str = "", category: str = ""):
        """Menyimpan atau memperbarui data konsep pengetahuan."""
        try:
            session = self.db.get_session()
            # Hapus duplikat key jika ada (seperti INSERT OR REPLACE)
            session.query(Knowledge).filter(Knowledge.key == key).delete()
            item = Knowledge(key=key, value=value, source=source, category=category)
            session.add(item)
            session.commit()
            session.close()
            self._emit_db_event("KnowledgeUpdated", "knowledge", {"key": key, "value": value})
        except Exception as e:
            log_warning(f"Memory: Gagal menyimpan knowledge: {e}")
            
    def get_all_knowledge(self) -> list:
        try:
            session = self.db.get_session()
            results = session.query(Knowledge.key, Knowledge.value, Knowledge.source, Knowledge.category, Knowledge.timestamp)\
                             .order_by(Knowledge.timestamp.desc()).all()
            session.close()
            return [(r.key, r.value, r.source, r.category, r.timestamp) for r in results]
        except Exception as e:
            log_warning(f"Memory: Gagal mengambil knowledge: {e}")
            return []

    # --- RESEARCH MEMORY ---
    def save_research(self, task_id: str, summary: str, files_referenced: str = ""):
        try:
            session = self.db.get_session()
            item = Research(task_id=task_id, summary=summary, files_referenced=files_referenced)
            session.add(item)
            session.commit()
            session.close()
            self._emit_db_event("MemoryUpdated", "research", {"task_id": task_id, "summary": summary})
        except Exception as e:
            log_warning(f"Memory: Gagal menyimpan research summary: {e}")
            
    def get_all_research(self) -> list:
        try:
            session = self.db.get_session()
            results = session.query(Research.task_id, Research.summary, Research.files_referenced, Research.timestamp)\
                             .order_by(Research.timestamp.desc()).all()
            session.close()
            return [(r.task_id, r.summary, r.files_referenced, r.timestamp) for r in results]
        except Exception as e:
            log_warning(f"Memory: Gagal mengambil research: {e}")
            return []

    # --- LONG TERM MEMORY ---
    def save_long_term(self, concept: str, detail: str, importance_score: int = 5):
        try:
            session = self.db.get_session()
            session.query(LongTerm).filter(LongTerm.concept == concept).delete()
            item = LongTerm(concept=concept, detail=detail, importance_score=importance_score)
            session.add(item)
            session.commit()
            session.close()
            self._emit_db_event("MemoryUpdated", "long_term", {"concept": concept})
        except Exception as e:
            log_warning(f"Memory: Gagal menyimpan long term memory: {e}")
            
    def get_all_long_term(self) -> list:
        try:
            session = self.db.get_session()
            results = session.query(LongTerm.concept, LongTerm.detail, LongTerm.importance_score, LongTerm.timestamp)\
                             .order_by(LongTerm.importance_score.desc()).all()
            session.close()
            return [(r.concept, r.detail, r.importance_score, r.timestamp) for r in results]
        except Exception as e:
            log_warning(f"Memory: Gagal mengambil long term memory: {e}")
            return []

    # --- RESET ALL MEMORIES ---
    def clear_all_memory(self):
        """Menghapus seluruh tabel memori (kosongkan data)."""
        try:
            session = self.db.get_session()
            session.query(Conversation).delete()
            session.query(Knowledge).delete()
            session.query(Research).delete()
            session.query(LongTerm).delete()
            session.query(EnglishProgress).delete()
            session.commit()
            session.close()
            self._emit_db_event("DatabaseChanged", "all", {"action": "clear"})
        except Exception as e:
            log_warning(f"Memory: Gagal menghapus database memori: {e}")

    # --- ENGLISH PROGRESS MEMORY ---
    def save_english_progress(self, level: str, vocab: int, grammar: int, writing: int):
        try:
            session = self.db.get_session()
            item = EnglishProgress(level=level, vocab_score=vocab, grammar_score=grammar, writing_score=writing)
            session.add(item)
            session.commit()
            session.close()
            self._emit_db_event("MemoryUpdated", "english_progress", {"level": level})
        except Exception as e:
            log_warning(f"Memory: Gagal menyimpan progress bahasa Inggris: {e}")

    def get_latest_english_progress(self) -> tuple:
        """Mengambil data tingkat kecakapan bahasa Inggris terakhir. Returns (level, vocab, grammar, writing)."""
        try:
            session = self.db.get_session()
            row = session.query(EnglishProgress.level, EnglishProgress.vocab_score, EnglishProgress.grammar_score, EnglishProgress.writing_score)\
                         .order_by(EnglishProgress.timestamp.desc()).first()
            session.close()
            return (row.level, row.vocab_score, row.grammar_score, row.writing_score) if row else ("B2", 50, 50, 50)
        except Exception as e:
            log_warning(f"Memory: Gagal mengambil progress bahasa Inggris: {e}")
            return ("B2", 50, 50, 50)
