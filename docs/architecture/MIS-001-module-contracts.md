# Module Interface Specification (MIS)
## MIS-001: Spesifikasi Kontrak Modul AI OS

**Tujuan**: Mendefinisikan antarmuka (interface) komunikasi antar-modul tingkat akar untuk menghilangkan *hard dependency*.

### 1. Kontrak `kernel`
Semua modul *harus* meregistrasikan diri melalui Dependency Injection ke Kernel.
```python
class IModule(Protocol):
    def boot(self) -> bool:
        """Inisialisasi internal modul."""
        ...
    def shutdown(self) -> None:
        """Pembersihan saat OS dimatikan."""
        ...
```

### 2. Kontrak `cognitive` (Pipeline Input)
Input pengguna tidak boleh langsung ke model. Harus melewati antarmuka `ICognitivePipeline`.
```python
class ICognitivePipeline(Protocol):
    def process_input(self, raw_input: str) -> dict:
        """Mengembalikan features (Tokens, Embeddings, TF-IDF)."""
        ...
    def process_output(self, prompt: str, generated: str) -> dict:
        """Mengembalikan hybrid_score dan flag safety."""
        ...
```

### 3. Kontrak `models` (AI Model Manager)
Sistem *routing* harus tidak peduli penyedia modelnya apa (Groq, Llama, Ollama).
```python
class IModelProvider(Protocol):
    def predict(self, context: dict, prompt: str) -> str:
        """Memanggil model spesifik dan mengembalikan teks."""
        ...
```

### 4. Kontrak `database` (Repository Pattern)
```python
class IRepository(Protocol):
    def get_by_id(self, id: str) -> dict: ...
    def save(self, entity: dict) -> bool: ...
```
