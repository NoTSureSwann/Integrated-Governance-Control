class ContextManager:
    """
    Modul sentral untuk menyatukan dan menyuplai data Context (Konteks)
    ke Agen AI sebelum memproses sebuah Task.
    
    Tipe Konteks yang didukung:
    - Conversation Context
    - Workspace Context
    - Repository Context
    - Knowledge Context
    - Memory Context
    - Dataset Context
    - Project Context
    - Plugin Context
    - Configuration Context
    """
    def __init__(self):
        self.active_contexts = {}

    def inject_context(self, context_type: str, data: dict):
        """Menyuntikkan data konteks terbaru ke dalam manager."""
        self.active_contexts[context_type] = data

    def build_prompt_context(self) -> str:
        """
        Merangkai seluruh data konteks yang aktif menjadi satu string
        yang dapat dipahami oleh LLM.
        """
        context_string = ""
        for ctx_type, data in self.active_contexts.items():
            context_string += f"\n--- [{ctx_type.upper()}] ---\n"
            for key, val in data.items():
                context_string += f"{key}: {val}\n"
        return context_string

# Global instance
kernel_context_manager = ContextManager()
