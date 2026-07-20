import unittest
import os
import sqlite3
from adapters.database.db_manager import DatabaseManager
from adapters.database.memory_adapter import MemoryRepositoryAdapter

class TestMemoryDatabase(unittest.TestCase):
    """
    Test Case untuk memverifikasi fungsionalitas DatabaseManager dan MemoryManager.
    """
    @classmethod
    def setUpClass(cls):
        # Gunakan database sementara khusus untuk testing
        cls.test_db_path = "database/test_nexus.db"
        cls.db_manager = DatabaseManager(db_path=cls.test_db_path)
        
        # Override db path di MemoryManager untuk pengujian
        cls.memory = MemoryRepositoryAdapter()
        cls.memory.db = cls.db_manager

    @classmethod
    def tearDownClass(cls):
        # Bersihkan file database test setelah selesai
        if os.path.exists(cls.test_db_path):
            try:
                os.remove(cls.test_db_path)
            except PermissionError:
                pass

    def setUp(self):
        # Bersihkan data di setiap tabel sebelum memulai tes individu
        self.memory.clear_all_memory()

    def test_database_initialization(self):
        """Memastikan database test berhasil dibuat dan semua tabel ada."""
        self.assertTrue(os.path.exists(self.test_db_path))
        
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        self.assertIn("conversations", tables)
        self.assertIn("knowledge", tables)
        self.assertIn("research", tables)
        self.assertIn("long_term", tables)
        self.assertIn("english_progress", tables)

    def test_conversation_memory(self):
        """Menguji operasi penyimpanan dan pemanggilan memori chat."""
        # Simpan pesan
        self.memory.save_message("user", "Hello Nexus!")
        self.memory.save_message("assistant", "Hello! How can I assist you?")
        
        # Ambil riwayat
        history = self.memory.get_conversation_history()
        self.assertEqual(len(history), 2)
        
        # Cek detail record pertama
        self.assertEqual(history[0][0], "user")
        self.assertEqual(history[0][1], "Hello Nexus!")
        
        # Cek detail record kedua
        self.assertEqual(history[1][0], "assistant")
        self.assertEqual(history[1][1], "Hello! How can I assist you?")

    def test_knowledge_memory(self):
        """Menguji penyimpanan, pengambilan, dan pemeriksaan duplikasi knowledge."""
        self.memory.save_knowledge("Python", "Bahasa pemrograman tingkat tinggi", "Wikipedia", "Coding")
        
        knows = self.memory.get_all_knowledge()
        self.assertEqual(len(knows), 1)
        self.assertEqual(knows[0][0], "Python")
        self.assertEqual(knows[0][1], "Bahasa pemrograman tingkat tinggi")
        
        # Uji penyimpanan ulang key yang sama (INSERT OR REPLACE)
        self.memory.save_knowledge("Python", "Bahasa pemrograman populer", "StackOverflow", "Coding")
        knows_updated = self.memory.get_all_knowledge()
        self.assertEqual(len(knows_updated), 1)
        self.assertEqual(knows_updated[0][1], "Bahasa pemrograman populer")
        self.assertEqual(knows_updated[0][2], "StackOverflow")

    def test_research_memory(self):
        """Menguji penyimpanan dan pemanggilan ringkasan riset berkas."""
        self.memory.save_research("Task-X", "Analisis performa model LLM", "docs/SIGMA.md")
        
        res = self.memory.get_all_research()
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0][0], "Task-X")
        self.assertEqual(res[0][1], "Analisis performa model LLM")
        self.assertEqual(res[0][2], "docs/SIGMA.md")

    def test_english_progress_memory(self):
        """Menguji pencatatan progres kecakapan bahasa Inggris CEFR."""
        # Secara default harus merespon B2 jika kosong
        default_lvl, _, _, _ = self.memory.get_latest_english_progress()
        self.assertEqual(default_lvl, "B2")
        
        # Simpan progres baru
        self.memory.save_english_progress("C1", 85, 90, 80)
        
        # Ambil progres terbaru
        level, vocab, grammar, writing = self.memory.get_latest_english_progress()
        self.assertEqual(level, "C1")
        self.assertEqual(vocab, 85)
        self.assertEqual(grammar, 90)
        self.assertEqual(writing, 80)

if __name__ == "__main__":
    unittest.main()
