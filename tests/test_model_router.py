import unittest
from models.router import ModelRouter
from adapters.llm.groq_adapter import GroqAdapter

class TestModelRouter(unittest.TestCase):
    def setUp(self):
        self.router = ModelRouter()

    def test_mock_completion(self):
        # Force mock mode and verify output
        res = self.router.complete(
            prompt="Hello!",
            system_prompt="System instructions",
            provider="Groq",
            model="llama3-model",
            mock=True
        )
        self.assertIn("[MOCK - Groq - llama3-model]", res)
        self.assertIn("Hello!", res)

    def test_mock_fallback_on_missing_key(self):
        # If API key is missing, it should fallback to mock completion
        import config
        old_key = config.GROQ_API_KEY
        config.GROQ_API_KEY = "" # Temporarily unset key
        try:
            res = self.router.complete(
                prompt="Test without key",
                provider="Groq",
                mock=False # Don't force mock, but key is missing
            )
            self.assertIn("[MOCK - Groq -", res)
        finally:
            config.GROQ_API_KEY = old_key

if __name__ == "__main__":
    unittest.main()
