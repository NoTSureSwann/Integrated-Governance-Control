from utils.logger import log_info, console
from rich.panel import Panel
from database.db_manager import DatabaseManager, Knowledge, DatasetMetadata

class GitHubAnalyzer:
    """
    Layer 17: Open Knowledge Connector (GitHub)
    Sesuai aturan PUBLIC DATA RULES, module ini bersifat READ ONLY.
    Tidak ada aksi mengubah, menghapus, commit, push, atau merge yang dilakukan
    tanpa authorization pengguna.
    """
    def __init__(self, mock: bool = False):
        self.mock = mock

    def analyze_repository(self, github_url: str) -> str:
        """
        Melakukan proses akuisisi data dan ekstraksi pengetahuan:
        1. Repository Structure Analysis
        2. README Analysis
        3. Source Code Analysis
        4. Dependency Analysis
        """
        log_info(f"Memulai koneksi READ ONLY ke repository: {github_url}")
        
        if self.mock:
            return self._run_mock_analysis(github_url)
            
        # Panggil connector asli
        from connectors.github_connector import nexus_github_connector
        clone_res = nexus_github_connector.clone_repository(github_url)
        
        if clone_res == "CLONE_BLOCKED":
            return "# GitHub Analysis Blocked\nUser denied permission to clone this repository."
        elif clone_res == "CLONE_FAILED":
            return "# GitHub Analysis Failed\nFailed to clone the repository. Check connection or URL."
            
        return self._generate_real_report(github_url)
        
    def _generate_real_report(self, github_url: str) -> str:
        db = DatabaseManager()
        
        # Query total files dari github_index
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT file_path FROM github_index WHERE repo_url = ?", (github_url,))
        files = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # Query datasets
        session = db.get_session()
        repo_name = github_url.split("/")[-1].replace(".git", "")
        datasets = session.query(DatasetMetadata).filter(DatasetMetadata.dataset_name.like(f"%[GitHub] {repo_name}%")).all()
        
        # Query parsed knowledge (markdown & python symbols)
        knowledge_entries = session.query(Knowledge).filter_by(source=github_url).all()
        session.close()
        
        # Group knowledge entries
        md_sections = [k for k in knowledge_entries if k.category == "Github-Knowledge"]
        code_symbols = [k for k in knowledge_entries if k.category == "Github-Code-Symbols"]
        
        # Build Markdown Report
        report = f"""# GitHub Repository Analysis: {repo_name}
        
**Target URL:** `{github_url}`
**Access Policy:** READ ONLY (Strict Compliance)

## 1. Repository Summary
Indexed a total of **{len(files)}** files successfully.

## 2. Dataset & Notebook Detection
"""
        if datasets:
            report += "The following datasets/notebooks were automatically detected and registered:\n"
            for ds in datasets:
                report += f"- **Dataset Name**: `{ds.dataset_name}`\n  - *Description*: {ds.description}\n  - *Source*: `{ds.source}`\n"
        else:
            report += "No datasets (CSV, JSON, JSONL, IPYNB) were detected in this repository.\n"
            
        report += "\n## 3. README & Markdown Structure\n"
        if md_sections:
            report += "Extracted sections from markdown documentation:\n"
            for sec in md_sections:
                header = sec.key.split("#")[-1]
                # Show first 150 chars of section body
                body_snippet = sec.value[:150].replace('\n', ' ') + "..." if len(sec.value) > 150 else sec.value
                report += f"- **{header}** (`{sec.key.split(':')[2].split('#')[0]}`):\n  > *{body_snippet}*\n"
        else:
            report += "No Markdown documentation sections found.\n"
            
        report += "\n## 4. Code Symbols Extraction (Python AST)\n"
        if code_symbols:
            report += "Parsed Python classes and functions:\n"
            for sym in code_symbols:
                sym_name = sym.key.split(":")[-1]
                file_origin = sym.key.split(":")[-2]
                report += f"- **{sym_name}** (in `{file_origin}`):\n"
                # Indent lines of symbol details
                indented_val = "\n".join("  " + line for line in sym.value.splitlines())
                report += f"{indented_val}\n"
        else:
            report += "No Python files or AST symbols detected.\n"
            
        return report

    def _run_mock_analysis(self, github_url: str) -> str:
        console.print(Panel(
            f"[bold green]Target URL:[/bold green] {github_url}\n"
            f"[bold cyan]Mode Akses:[/bold cyan] FETCH & CLONE (READ ONLY)\n"
            f"[bold yellow]Tahapan Analisis:[/bold yellow] Struktur, README, Code, Dependency, Knowledge Graph...",
            title="[bold blue]GITHUB ANALYZER[/bold blue]",
            border_style="blue"
        ))
        
        return f"""# GitHub Analyzer Output
 
**Target Repository:** `{github_url}`
**Access Policy:** READ ONLY (Strict Compliance)
 
## 1. Repository Summary
Repository ini memiliki struktur pengembangan perangkat lunak terstandarisasi. Komponen utama dibagi ke dalam modul-modul fungsional yang jelas (berbasis paradigma Object-Oriented).
 
## 2. Architecture & Important Modules
- **Root Level**: Terdapat file konfigurasi standar seperti `.gitignore`, `README.md`, dan file manajemen dependensi.
- **Source Code (`src/` atau ekuivalen)**: Logika inti dipisahkan berdasarkan domain bisnis.
- **Tests**: Modul pengujian tersedia, menunjukkan penerapan *Test-Driven* atau *Continuous Integration*.
 
## 3. Dependency Graph & Keywords
- **Dependencies**: Menggunakan pustaka *open-source* modern yang lazim di ekosistemnya.
- **Keywords Ekstraksi**: `Modular`, `Extensible`, `Scalable`, `API-driven`.
- **Knowledge Graph Mapping**: `Repository` -> `Modules` -> `Classes` -> `Methods` telah diindeks di dalam *Working Memory*.
 
## 4. Improvement & Risk
- **Risk**: Ditemukan beberapa pola *Anti-Pattern* ringan pada duplikasi logika di modul utilitas.
- **Recommended Reading**: Agent terkait direkomendasikan membaca `README.md` secara mendalam sebelum menyusun solusi spesifik.
"""
