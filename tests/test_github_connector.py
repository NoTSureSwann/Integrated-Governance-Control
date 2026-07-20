import unittest
import os
import shutil
import uuid
from unittest.mock import patch
from connectors.github_connector import GitHubConnector
from adapters.database.db_manager import DatabaseManager

class TestGitHubConnector(unittest.TestCase):
    def setUp(self):
        self.workspace_dir = f"workspace/test_clones_{uuid.uuid4().hex[:8]}"
        self.connector = GitHubConnector(workspace_dir=self.workspace_dir)
        db = DatabaseManager()
        
    def tearDown(self):
        # Bersihkan folder test
        if os.path.exists(self.workspace_dir):
            shutil.rmtree(self.workspace_dir, ignore_errors=True)
            
    def test_clone_and_index(self):
        # Gunakan repo kecil publik untuk test integrasi (octocat/Hello-World)
        repo_url = "https://github.com/octocat/Hello-World.git"
        target_dir = self.connector.clone_repository(repo_url, branch="master")
        
        # Verifikasi clone
        self.assertTrue(os.path.exists(target_dir))
        
        # Verifikasi di dalam database indexing (Layer 27 Requirement)
        db = DatabaseManager()
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM github_index WHERE repo_url = ?", (repo_url,))
        rows = cursor.fetchall()
        conn.close()
        
        self.assertGreater(len(rows), 0, "Repository gagal diindeks ke dalam SQLite")
        has_readme = any("README" in str(row[2]) for row in rows)
        self.assertTrue(has_readme, "File README tidak ditemukan dalam indeks database")
        
    def test_indexing_and_parsing_local(self):
        # Setup local mock repo folder
        mock_repo_dir = os.path.join(self.workspace_dir, "mock-repo")
        os.makedirs(mock_repo_dir, exist_ok=True)
        
        # Create a Python file
        py_content = """
def sample_func(a, b):
    \"\"\"This is a test function.\"\"\"
    return a + b

class SampleClass:
    \"\"\"This is a test class.\"\"\"
    def method_one(self):
        pass
"""
        with open(os.path.join(mock_repo_dir, "script.py"), "w", encoding="utf-8") as f:
            f.write(py_content)
            
        # Create a Markdown file
        md_content = """# Title
Some description here.
## Section A
Details of Section A.
"""
        with open(os.path.join(mock_repo_dir, "README.md"), "w", encoding="utf-8") as f:
            f.write(md_content)
            
        # Create a CSV dataset
        csv_content = "id,name,value\n1,alice,10\n2,bob,20\n"
        with open(os.path.join(mock_repo_dir, "data.csv"), "w", encoding="utf-8") as f:
            f.write(csv_content)
            
        repo_url = "https://github.com/test/mock-repo.git"
        self.connector._index_repository(repo_url, mock_repo_dir)
        
        # Verify database contents
        db = DatabaseManager()
        session = db.get_session()
        
        # Check Knowledge entries (Markdown sections)
        from adapters.database.db_manager import Knowledge, DatasetMetadata
        
        intro_knowledge = session.query(Knowledge).filter_by(key="github:mock-repo:README.md#Title").first()
        self.assertIsNotNone(intro_knowledge)
        self.assertIn("Some description here.", intro_knowledge.value)
        
        sec_a_knowledge = session.query(Knowledge).filter_by(key="github:mock-repo:README.md#Section A").first()
        self.assertIsNotNone(sec_a_knowledge)
        self.assertIn("Details of Section A.", sec_a_knowledge.value)
        
        # Check Python symbols
        func_knowledge = session.query(Knowledge).filter_by(key="github:mock-repo:script.py:sample_func").first()
        self.assertIsNotNone(func_knowledge)
        self.assertIn("This is a test function.", func_knowledge.value)
        
        class_knowledge = session.query(Knowledge).filter_by(key="github:mock-repo:script.py:SampleClass").first()
        self.assertIsNotNone(class_knowledge)
        self.assertIn("method_one", class_knowledge.value)
        
        # Check Dataset registration
        dataset_meta = session.query(DatasetMetadata).filter_by(dataset_name="[GitHub] mock-repo/data.csv").first()
        self.assertIsNotNone(dataset_meta)
        self.assertIn("Auto-detected dataset", dataset_meta.description)
        
        session.close()

    @patch('services.hook_manager.nexus_hook_manager.execute_hooks')
    def test_clone_blocked_by_auth(self, mock_hooks):
        # Simulasikan pengguna memblokir (Cancel) pada dialog Otorisasi
        mock_hooks.return_value = {"status": "blocked"}
        
        repo_url = "https://github.com/octocat/Spoon-Knife.git"
        result = self.connector.clone_repository(repo_url)
        
        self.assertEqual(result, "CLONE_BLOCKED")
        self.assertFalse(os.path.exists(os.path.join(self.workspace_dir, "Spoon-Knife")))

if __name__ == "__main__":
    unittest.main()
