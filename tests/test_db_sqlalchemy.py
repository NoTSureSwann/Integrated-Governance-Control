import unittest
from database.db_manager import DatabaseManager, Conversation, Knowledge
from sqlalchemy.orm import Session

class TestDBSqlAlchemy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Gunakan in-memory SQLite database untuk testing cepat
        cls.db = DatabaseManager(db_path=":memory:")

    def test_orm_operations(self):
        session = self.db.get_session()
        self.assertIsInstance(session, Session)
        
        # Test Insert
        conv = Conversation(role="user", content="Hello database!")
        session.add(conv)
        session.commit()
        
        # Test Query
        retrieved = session.query(Conversation).filter_by(role="user").first()
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.content, "Hello database!")
        
        # Test Delete
        session.delete(retrieved)
        session.commit()
        
        retrieved_after_delete = session.query(Conversation).filter_by(role="user").first()
        self.assertIsNone(retrieved_after_delete)
        
        session.close()

    def test_dataset_metadata_orm(self):
        from database.db_manager import DatasetMetadata
        session = self.db.get_session()
        
        # Test Insert
        dataset = DatasetMetadata(
            dataset_name="test_dataset",
            author="Nexus",
            license="MIT",
            language="en",
            description="A test dataset"
        )
        session.add(dataset)
        session.commit()
        
        # Test Query
        retrieved = session.query(DatasetMetadata).filter_by(dataset_name="test_dataset").first()
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.author, "Nexus")
        self.assertEqual(retrieved.version, "1.0.0")
        
        session.close()

if __name__ == "__main__":
    unittest.main()
