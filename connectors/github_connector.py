import os
import subprocess
import shutil
import hashlib
import ast
import re
from typing import Dict, Any, List
from utils.logger import log_info, log_error, log_warning
from adapters.database.db_manager import DatabaseManager, Knowledge, DatasetMetadata, GithubIndex
from services.hook_manager import nexus_hook_manager

class GitHubConnector:
    """
    Layer 27: GITHUB CONNECTOR
    Mendukung HTTPS, Git CLI, Repository API.
    Aksi ini bersifat READ ONLY (Clone) dan wajib diindeks sebelum diproses AI.
    """
    def __init__(self, workspace_dir: str = "workspace/github_clones"):
        self.workspace_dir = workspace_dir
        os.makedirs(self.workspace_dir, exist_ok=True)
        
    def clone_repository(self, repo_url: str, auth_method: str = "HTTPS", branch: str = "main") -> str:
        """
        Kloning repository secara READ ONLY (depth=1).
        Memerlukan Otorisasi melalui Hook Engine sebelum dieksekusi.
        """
        # Hook authorization: memblokir jika pengguna membatalkan
        ctx = nexus_hook_manager.execute_hooks("before_repository", {
            "action": "clone", 
            "repo_url": repo_url,
            "branch": branch
        })
        
        # Jika ctx mengembalikan status "blocked", batalkan proses.
        if ctx.get("status") == "blocked" or getattr(ctx.get("auth_response", None), "is_blocked", False):
            log_warning(f"Kloning diblokir oleh otorisasi pengguna: {repo_url}")
            return "CLONE_BLOCKED"

        repo_name = repo_url.split("/")[-1].replace(".git", "")
        target_dir = os.path.join(self.workspace_dir, repo_name)
        
        # Bersihkan direktori lama jika sudah ada (karena read only)
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir, ignore_errors=True)
            
        try:
            # Menggunakan Git CLI
            cmd = ["git", "clone", "--branch", branch, "--depth", "1", repo_url, target_dir]
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            log_info(f"Berhasil clone repository READ ONLY: {repo_url}")
            
            # Wajib Indexing sebelum diproses (Aturan Layer 27)
            self._index_repository(repo_url, target_dir)
            
            # Hook setelah clone dan indeks selesai
            nexus_hook_manager.execute_hooks("after_repository", {
                "action": "clone_success",
                "repo_url": repo_url
            })
            return target_dir
        except subprocess.CalledProcessError as e:
            log_error(f"Gagal melakukan clone {repo_url}: {e.stderr}")
            return "CLONE_FAILED"
            
    def _index_repository(self, repo_url: str, repo_dir: str):
        """Memindai isi file teks dalam repo dan menyimpannya ke github_index SQLite."""
        log_info(f"Memulai indexing repository {repo_url} ke dalam database...")
        db = DatabaseManager()
        session = db.get_session()
        
        try:
            # Hapus indeks lama jika ada (agar tidak duplicate)
            session.query(GithubIndex).filter_by(repo_url=repo_url).delete()
            session.commit()
            
            indexed_files = 0
            for root, dirs, files in os.walk(repo_dir):
                if ".git" in root:
                    continue
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, repo_dir)
                    
                    # Dataset & Notebook Detection
                    ext = os.path.splitext(file)[1].lower()
                    if ext in ('.csv', '.json', '.jsonl', '.ipynb'):
                        self._register_dataset(session, repo_url, rel_path, file_path)
                        
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            
                        file_hash = hashlib.md5(content.encode()).hexdigest()
                        idx_entry = GithubIndex(
                            repo_url=repo_url,
                            file_path=rel_path,
                            content=content,
                            hash=file_hash
                        )
                        session.add(idx_entry)
                        indexed_files += 1
                        
                        # Markdown Parsing
                        if ext == '.md':
                            self._parse_markdown_to_knowledge(session, repo_url, rel_path, content)
                        # Python Parsing
                        elif ext == '.py':
                            self._parse_python_to_knowledge(session, repo_url, rel_path, content)
                            
                    except UnicodeDecodeError:
                        # Lewati file binary (misal gambar, dll)
                        pass
                    except Exception as e:
                        log_warning(f"Gagal membaca file {file_path}: {e}")
                        
            session.commit()
            log_info(f"Indexing repository {repo_url} selesai. Total {indexed_files} file diindeks.")
        except Exception as e:
            session.rollback()
            log_error(f"Gagal melakukan indexing repository: {e}")
        finally:
            session.close()

    def _register_dataset(self, session, repo_url: str, rel_path: str, abs_path: str):
        """Auto-register detected dataset in dataset_metadata."""
        try:
            repo_name = repo_url.split("/")[-1].replace(".git", "")
            dataset_name = f"[GitHub] {repo_name}/{rel_path}"
            
            existing = session.query(DatasetMetadata).filter_by(dataset_name=dataset_name).first()
            if not existing:
                meta = DatasetMetadata(
                    dataset_name=dataset_name,
                    author="GitHub Repository",
                    license="Unknown",
                    version="1.0.0",
                    language="en",
                    description=f"Auto-detected dataset in {repo_url} at {rel_path}",
                    source=f"file:///{abs_path.replace(os.sep, '/')}"
                )
                session.add(meta)
                log_info(f"Registered dataset metadata: {dataset_name}")
        except Exception as e:
            log_warning(f"Gagal meregistrasi dataset {rel_path}: {e}")

    def _parse_markdown_to_knowledge(self, session, repo_url: str, rel_path: str, content: str):
        """Parse markdown headers and content, save to Knowledge table."""
        try:
            sections = re.split(r'\n(?=#+ )', "\n" + content)
            repo_name = repo_url.split("/")[-1].replace(".git", "")
            for section in sections:
                section = section.strip()
                if not section:
                    continue
                header_match = re.match(r'^(#+)\s+(.*)$', section, re.MULTILINE)
                if header_match:
                    header_title = header_match.group(2).strip()
                    section_body = section[header_match.end():].strip()
                else:
                    header_title = "Intro"
                    section_body = section
                
                if not section_body:
                    continue
                
                key = f"github:{repo_name}:{rel_path}#{header_title}"[:255]
                existing = session.query(Knowledge).filter_by(key=key).first()
                if existing:
                    existing.value = section_body
                else:
                    knowledge_entry = Knowledge(
                        key=key,
                        value=section_body,
                        source=repo_url,
                        category="Github-Knowledge"
                    )
                    session.add(knowledge_entry)
        except Exception as e:
            log_warning(f"Gagal memparsing markdown {rel_path}: {e}")

    def _parse_python_to_knowledge(self, session, repo_url: str, rel_path: str, content: str):
        """Parse Python file using AST to extract classes, functions and docstrings."""
        try:
            tree = ast.parse(content)
            repo_name = repo_url.split("/")[-1].replace(".git", "")
            
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.ClassDef):
                    class_name = node.name
                    docstring = ast.get_docstring(node) or "No docstring provided."
                    methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    
                    value = f"Class: {class_name}\nDocstring: {docstring}\nMethods: {', '.join(methods)}"
                    key = f"github:{repo_name}:{rel_path}:{class_name}"[:255]
                    
                    existing = session.query(Knowledge).filter_by(key=key).first()
                    if existing:
                        existing.value = value
                    else:
                        entry = Knowledge(
                            key=key,
                            value=value,
                            source=repo_url,
                            category="Github-Code-Symbols"
                        )
                        session.add(entry)
                        
                elif isinstance(node, ast.FunctionDef):
                    func_name = node.name
                    docstring = ast.get_docstring(node) or "No docstring provided."
                    args = [arg.arg for arg in node.args.args]
                    
                    value = f"Function: {func_name}({', '.join(args)})\nDocstring: {docstring}"
                    key = f"github:{repo_name}:{rel_path}:{func_name}"[:255]
                    
                    existing = session.query(Knowledge).filter_by(key=key).first()
                    if existing:
                        existing.value = value
                    else:
                        entry = Knowledge(
                            key=key,
                            value=value,
                            source=repo_url,
                            category="Github-Code-Symbols"
                        )
                        session.add(entry)
        except Exception as e:
            log_warning(f"Gagal memparsing python {rel_path}: {e}")
        
    def fetch_api_metadata(self, repo_url: str) -> Dict[str, Any]:
        """Memanggil Repository API via HTTP Requests untuk Actions, PR, Issue, dll."""
        # Pada sistem produksi penuh, fungsi ini akan memanggil API GitHub menggunakan GITHUB_TOKEN
        return {
            "url": repo_url,
            "issues_count": 0,
            "prs_count": 0,
            "releases": [],
            "readme_available": True
        }

# Singleton instance
nexus_github_connector = GitHubConnector()
