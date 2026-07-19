# Layer 17: Open Knowledge Connector
# Digunakan untuk integrasi ke sumber data publik (GitHub, PDF, Web) secara READ ONLY.

from .github_analyzer import GitHubAnalyzer

__all__ = ["GitHubAnalyzer"]
