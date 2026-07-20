class PreprocessingModule:
    """
    Modul Pra-pemrosesan Teks untuk membersihkan dan menormalkan input.
    """
    def __init__(self):
        pass

    def run_pipeline(self, text: str) -> dict:
        """
        Menjalankan seluruh tahap preprocessing teks.
        Mengembalikan struktur data dengan teks yang sudah dinormalkan
        dan metadata tambahan.
        """
        result = {
            "original_text": text,
            "normalized_text": self.normalize(text),
            "tokens": self.tokenize(text),
            "language": self.detect_language(text),
            "metadata": {
                "has_code_blocks": self.detect_code_blocks(text),
                "has_urls": self.detect_urls(text)
            }
        }
        return result

    def normalize(self, text: str) -> str:
        # Placeholder untuk Unicode Normalization, Case Folding, Noise Removal
        return text.strip().lower()

    def tokenize(self, text: str) -> list:
        # Placeholder untuk pemotongan kata
        return text.split()

    def detect_language(self, text: str) -> str:
        # Placeholder
        return "id"

    def detect_code_blocks(self, text: str) -> bool:
        # Placeholder deteksi blok kode Markdown
        return "```" in text

    def detect_urls(self, text: str) -> bool:
        return "http://" in text or "https://" in text
