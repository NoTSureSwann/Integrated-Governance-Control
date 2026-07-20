"""
Domain Registry Module - Project Nexus DAE v1.0
Menyimpan registrasi domain terpercaya, authority score, dan pemetaan sektor.
"""

DOMAIN_SECTORS = {
    "academic": [
        "arxiv.org", "openalex.org", "crossref.org", "semanticscholar.org",
        "doaj.org", "pubmed.ncbi.nlm.nih.gov", "plos.org", "nature.com",
        "springer.com", "sciencedirect.com", "mdpi.com", "ieee.org", "acm.org"
    ],
    "knowledge": [
        "wikipedia.org", "wikidata.org", "dbpedia.org", "archive.org",
        "gutenberg.org", "loc.gov"
    ],
    "programming": [
        "github.com", "gitlab.com", "codeberg.org", "huggingface.co",
        "pypi.org", "npmjs.com", "docker.com", "readthedocs.io", "devdocs.io"
    ],
    "documentation": [
        "python.org", "fastapi.tiangolo.com", "docs.sqlalchemy.org",
        "doc.qt.io", "sqlite.org", "redis.io", "postgresql.org", "kubernetes.io"
    ],
    "government_id": [
        "bps.go.id", "brin.go.id", "kemdikbud.go.id", "kemkes.go.id",
        "bssn.go.id", "jdih.go.id", "bi.go.id", "ojk.go.id", "data.go.id", "satudata.go.id"
    ],
    "government_int": [
        "nist.gov", "europa.eu", "oecd.org", "unesco.org", "un.org",
        "who.int", "worldbank.org", "imf.org", "data.gov", "data.europa.eu"
    ],
    "ai_research": [
        "openai.com", "anthropic.com", "deepmind.google", "ai.meta.com",
        "mistral.ai", "cohere.com", "ollama.ai", "langchain.com", "llamaindex.ai", "huggingface.co"
    ],
    "benchmarks": [
        "paperswithcode.com", "huggingface.co/datasets", "mteb.dev", "mlcommons.org", "kaggle.com"
    ],
    "economics": [
        "fred.stlouisfed.org", "worldbank.org", "imf.org", "oecd.org",
        "tradingeconomics.com", "bi.go.id", "ojk.go.id", "idx.co.id"
    ],
    "cefr_english": [
        "cambridge.org", "britishcouncil.org", "bbc.co.uk",
        "learningenglish.voanews.com", "ted.com", "teded.com", "oxfordlearnersdictionaries.com"
    ],
    "cybersecurity": [
        "mitre.org", "owasp.org", "cve.org", "cisa.gov", "first.org"
    ],
    "robotics": [
        "ros.org", "openrobotics.org", "gazebosim.org", "webots.cloud", "opencv.org", "nvidia.com"
    ]
}

def get_sector_for_url(url: str) -> str:
    """Mendeteksi sektor berdasarkan domain URL."""
    url_lower = url.lower()
    for sector, domains in DOMAIN_SECTORS.items():
        for domain in domains:
            if domain in url_lower:
                return sector
    return "general"

def calculate_domain_authority(url: str) -> float:
    """Menghitung skor otoritas domain (0.0 - 1.0)."""
    sector = get_sector_for_url(url)
    authority_map = {
        "academic": 0.95,
        "government_id": 0.90,
        "government_int": 0.92,
        "cybersecurity": 0.90,
        "ai_research": 0.88,
        "documentation": 0.85,
        "programming": 0.82,
        "economics": 0.85,
        "benchmarks": 0.85,
        "knowledge": 0.80,
        "cefr_english": 0.80,
        "robotics": 0.85,
        "general": 0.50
    }
    return authority_map.get(sector, 0.50)
