import os
import time
from typing import Dict, List, Any
from utils.logger import log_info, log_warning
from connectors.url_fetcher import url_fetcher
from connectors.domain_registry import get_sector_for_url

class DataAcquisitionEngine:
    """
    Data Acquisition Engine (DAE) Core v1.0
    Mengorkestrasikan akuisisi data (Search, Fetch, Validate, Deduplicate, Store, Index)
    secara real-time & batch.
    """
    def __init__(self, base_dir: str = "."):
        self.base_dir = base_dir
        self.processed_hashes = set()

    def acquire_from_url(self, url: str) -> Dict[str, Any]:
        """
        Alur Eksekusi DAE:
        Search/Fetch -> Hash Check -> Deduplicate -> Validate -> Normalize -> Store to Knowledge Sector
        """
        # 1. Fetch
        result = url_fetcher.fetch_url(url)
        if not result["success"]:
            return result

        metadata = result["metadata"]
        sha256 = metadata["sha256"]

        # 2. Deduplicate
        if sha256 in self.processed_hashes:
            log_info(f"[DAE] Duplicate data detected for {url} (SHA256: {sha256[:8]}). Skipping store.")
            return {
                "success": True,
                "duplicate": True,
                "metadata": metadata
            }

        self.processed_hashes.add(sha256)

        # 3. Store to target sector folder
        sector = metadata["sector"]
        target_dir = os.path.join(self.base_dir, "knowledge", "documents", sector)
        os.makedirs(target_dir, exist_ok=True)

        safe_filename = f"acquired_{int(time.time())}_{sha256[:8]}.txt"
        file_path = os.path.join(target_dir, safe_filename)

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"--- METADATA ---\n")
                f.write(f"URL: {url}\n")
                f.write(f"Title: {metadata['title']}\n")
                f.write(f"Sector: {sector}\n")
                f.write(f"Authority Score: {metadata['authority_score']}\n")
                f.write(f"SHA256: {sha256}\n")
                f.write(f"--- CONTENT ---\n\n")
                f.write(result["content"])

            log_info(f"[DAE] Successfully acquired and stored data to {file_path}")
            metadata["saved_path"] = file_path
            return {
                "success": True,
                "duplicate": False,
                "metadata": metadata
            }
        except Exception as e:
            log_warning(f"[DAE] Failed to write acquired file: {e}")
            return {"success": False, "error": str(e)}

    def batch_acquire_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Proses akuisisi masal untuk beberapa URL."""
        results = []
        for url in urls:
            res = self.acquire_from_url(url)
            results.append(res)
        return results

# Global DAE instance
dae_engine = DataAcquisitionEngine()
