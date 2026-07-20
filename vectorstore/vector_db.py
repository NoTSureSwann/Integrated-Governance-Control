import time
from typing import List, Dict, Any
from utils.logger import log_info, log_warning
from cognitive.ingestion_engine import ingestion_engine
from vectorstore.embeddings import TFIDFEmbedder

class VectorDatabase:
    """
    In-Memory Vector Database v1.0
    Mengelola indexing (pengindeksan) dokumen teks dan meretrieve 
    dokumen paling relevan berdasarkan Semantic Search (TF-IDF Cosine Similarity).
    """
    def __init__(self):
        self.embedder = TFIDFEmbedder()
        self.documents = []  # List of raw text contents
        self.metadata = []   # List of dicts (filename, sector, etc)
        self.last_indexed = 0

    def build_index(self) -> None:
        """
        Mengambil semua dokumen via Ingestion Engine dan mem-build Vector Matrix.
        """
        log_info("[VectorDatabase] Building Semantic Search Index...")
        
        # 1. Scan semua sektor knowledge
        scan_result = ingestion_engine.scan_all_sources()
        docs_summary = scan_result.get("documents", {})

        self.documents.clear()
        self.metadata.clear()

        # 2. Load konten setiap file
        for sector, files in docs_summary.items():
            for filename in files:
                # Lewati file dot (hidden)
                if filename.startswith("."):
                    continue
                    
                content = ingestion_engine.load_document(sector, filename)
                if content.strip():
                    self.documents.append(content)
                    self.metadata.append({
                        "filename": filename,
                        "sector": sector,
                        "length": len(content)
                    })

        # 3. Fit Transform Vectorizer
        if self.documents:
            self.embedder.fit_transform(self.documents)
            self.last_indexed = time.time()
            log_info(f"[VectorDatabase] Indexed {len(self.documents)} documents successfully.")
        else:
            log_warning("[VectorDatabase] No documents found to index.")

    def search(self, query: str, top_k: int = 3, threshold: float = 0.05) -> List[Dict[str, Any]]:
        """
        Melakukan Semantic Search pada memori dan mengembalikan top-K dokumen 
        yang memiliki similarity di atas threshold.
        """
        if not self.documents or not self.embedder.is_fitted:
            log_warning("[VectorDatabase] Search failed: Index is empty or not built.")
            return []

        # Hitung similarity semua dokumen terhadap query
        similarities = self.embedder.calculate_similarities(query)

        # Gabungkan score dengan index dokumen
        scored_docs = list(enumerate(similarities))
        
        # Sortir descending berdasarkan score
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        results = []
        for doc_idx, score in scored_docs[:top_k]:
            if score >= threshold:
                results.append({
                    "score": score,
                    "content": self.documents[doc_idx],
                    "metadata": self.metadata[doc_idx]
                })

        return results

# Global Instance
vector_db = VectorDatabase()
