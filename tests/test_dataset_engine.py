import unittest
import pandas as pd
import os
from services.dataset_engine import DatasetEngine

class TestDatasetEngine(unittest.TestCase):
    def setUp(self):
        self.engine = DatasetEngine()
        self.test_csv = "test_data.csv"
        self.test_json = "test_data.json"
        
        # Buat dummy data
        data = {
            "instruction": ["Translate to French", "Summarize this"],
            "input": ["Hello world", "Nexus is an AI OS that connects everything"],
            "output": ["Bonjour le monde", "Nexus is a unified AI platform"]
        }
        self.df = pd.DataFrame(data)
        self.df.to_csv(self.test_csv, index=False)
        self.df.to_json(self.test_json, orient='records')

    def tearDown(self):
        if os.path.exists(self.test_csv):
            os.remove(self.test_csv)
        if os.path.exists(self.test_json):
            os.remove(self.test_json)

    def test_load_csv(self):
        self.assertTrue(self.engine.load_dataset(self.test_csv))
        self.assertIsNotNone(self.engine.df)
        self.assertEqual(len(self.engine.df), 2)

    def test_overview(self):
        self.engine.load_dataset(self.test_csv)
        overview = self.engine.get_overview()
        self.assertEqual(overview["rows"], 2)
        self.assertEqual(overview["columns"], 3)
        self.assertIn("instruction", overview["columns_list"])

    def test_deduplicate(self):
        self.engine.load_dataset(self.test_csv)
        # Tambahkan duplicate manual
        self.engine.df = pd.concat([self.engine.df, self.engine.df.iloc[[0]]])
        self.assertEqual(len(self.engine.df), 3)
        self.engine.deduplicate()
        self.assertEqual(len(self.engine.df), 2)

    def test_prepare_instruction_dataset(self):
        self.engine.load_dataset(self.test_csv)
        success = self.engine.prepare_instruction_dataset("instruction", "input", "output")
        self.assertTrue(success)
        self.assertIn("instruction", self.engine.df.columns)
        self.assertIn("input", self.engine.df.columns)
        self.assertIn("output", self.engine.df.columns)

if __name__ == "__main__":
    unittest.main()
