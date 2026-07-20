import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple

class TFIDFEmbedder:
    """
    In-memory TF-IDF Embedder v1.0
    Berfungsi untuk mengubah dokumen menjadi vektor matematika
    dan menghitung kedekatan (similarity) berbasis Cosine Similarity.
    """
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            lowercase=True,
            max_df=0.85,
            min_df=1
        )
        self.document_vectors = None
        self.is_fitted = False

    def fit_transform(self, documents: List[str]) -> None:
        """
        Mempelajari vokabuler dari corpus dan membangun matrix TF-IDF (Sparse Matrix).
        """
        if not documents:
            self.document_vectors = None
            self.is_fitted = False
            return
            
        self.document_vectors = self.vectorizer.fit_transform(documents)
        self.is_fitted = True

    def calculate_similarities(self, query: str) -> List[float]:
        """
        Mengubah query menjadi vektor dan menghitung Cosine Similarity 
        terhadap seluruh dokumen yang ada di indeks.
        """
        if not self.is_fitted or self.document_vectors is None:
            return []

        # Transform query ke vector space yang sama
        query_vector = self.vectorizer.transform([query])
        
        # Hitung cosine similarity
        similarities = cosine_similarity(query_vector, self.document_vectors)
        
        # Flatten array ke List[float]
        return similarities[0].tolist()
