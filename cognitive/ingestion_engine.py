import os
import json
import csv
from typing import Dict, List, Any
from utils.logger import log_info, log_warning

class DataIngestionEngine:
    """
    Data Ingestion Engine v1.0
    Memindai dan membaca berkas dari datasets/raw/ dan knowledge/documents/
    berdasarkan sektor (reasoning, knowledge, social, economic, riset_teknologi, source_code, governance_policy, cefr_english, benchmarks_eval).
    """
    def __init__(self, base_dir: str = "."):
        self.base_dir = base_dir
        self.datasets_dir = os.path.join(base_dir, "datasets", "raw")
        self.documents_dir = os.path.join(base_dir, "knowledge", "documents")

    def scan_all_sources(self) -> Dict[str, Any]:
        """
        Memindai seluruh direktori data dan mengembalikan ringkasan jumlah berkas per sektor.
        """
        summary = {
            "datasets": self._scan_directory(self.datasets_dir),
            "documents": self._scan_directory(self.documents_dir)
        }
        log_info(f"[IngestionEngine] Completed scan. Found {sum(len(v) for v in summary['datasets'].values())} datasets and {sum(len(v) for v in summary['documents'].values())} documents.")
        return summary

    def _scan_directory(self, root_path: str) -> Dict[str, List[str]]:
        sector_files = {}
        if not os.path.exists(root_path):
            return sector_files

        for sector in os.listdir(root_path):
            sector_path = os.path.join(root_path, sector)
            if os.path.isdir(sector_path):
                files = [
                    f for f in os.listdir(sector_path)
                    if not f.startswith(".") and os.path.isfile(os.path.join(sector_path, f))
                ]
                sector_files[sector] = files
        return sector_files

    def load_document(self, sector: str, filename: str) -> str:
        """Membaca isi dokumen teks/markdown dari knowledge/documents/<sector>/<filename>."""
        file_path = os.path.join(self.documents_dir, sector, filename)
        if not os.path.exists(file_path):
            log_warning(f"[IngestionEngine] Document not found: {file_path}")
            return ""

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            log_warning(f"[IngestionEngine] Failed to read {file_path}: {e}")
            return ""

    def load_dataset_json(self, sector: str, filename: str) -> Any:
        """Membaca dataset JSON dari datasets/raw/<sector>/<filename>."""
        file_path = os.path.join(self.datasets_dir, sector, filename)
        if not os.path.exists(file_path):
            log_warning(f"[IngestionEngine] Dataset not found: {file_path}")
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log_warning(f"[IngestionEngine] Failed to load JSON {file_path}: {e}")
            return None

# Global instance
ingestion_engine = DataIngestionEngine()
