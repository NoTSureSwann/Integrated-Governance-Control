import hashlib
import re
import urllib.request
import urllib.parse
from typing import Dict, Any
from utils.logger import log_info, log_warning
from connectors.domain_registry import get_sector_for_url, calculate_domain_authority

class URLFetcher:
    """
    URL Fetcher & Parser Connector v1.0
    Mengambil konten dari URL, membersihkan tag HTML, menghitung SHA256,
    serta melakukan klasifikasi sektor dan pembuatan metadata.
    """
    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def fetch_url(self, url: str) -> Dict[str, Any]:
        """
        Mengambil konten dari URL, menormalkan teks, dan menghitung skor keandalan (Reliability Score).
        """
        log_info(f"[URLFetcher] Fetching URL: {url}")
        headers = {
            "User-Agent": "Nexus-DAE/1.0 (AI OS Data Acquisition Engine; +https://github.com/NoTSureSwann/Integrated-Governance-Control)"
        }

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                html_content = response.read().decode('utf-8', errors='ignore')
                
            clean_text = self._clean_html(html_content)
            sha256_hash = hashlib.sha256(clean_text.encode('utf-8')).hexdigest()
            sector = get_sector_for_url(url)
            auth_score = calculate_domain_authority(url)

            metadata = {
                "url": url,
                "sector": sector,
                "sha256": sha256_hash,
                "authority_score": auth_score,
                "length": len(clean_text),
                "title": self._extract_title(html_content)
            }

            return {
                "success": True,
                "metadata": metadata,
                "content": clean_text
            }
        except Exception as e:
            log_warning(f"[URLFetcher] Error fetching {url}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "metadata": {"url": url, "authority_score": 0.0}
            }

    def _clean_html(self, html: str) -> str:
        """Pembersih HTML ke teks polos."""
        text = re.sub(r'<script.*?>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style.*?>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<.*?>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _extract_title(self, html: str) -> str:
        match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else "No Title"

# Global instance
url_fetcher = URLFetcher()
