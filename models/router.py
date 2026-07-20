import os
import config
from utils.logger import log_info, log_warning
from ports.agent_port import IAgentProvider
from adapters.llm.groq_adapter import GroqAdapter

class ModelRouter:
    """
    Layer 6: MODEL ROUTER (Hexagonal Architecture Edition)
    Menangani pendaftaran dan eksekusi Provider LLM (Adapters).
    """
    def __init__(self):
        self._providers = {}
        self._register_default_providers()

    def _register_default_providers(self):
        # Registrasi adapter bawaan
        self.register_provider(GroqAdapter(
            api_key=config.GROQ_API_KEY_1, 
            model_name=config.GROQ_MODEL_1, 
            provider_name="Groq1"
        ))
        self.register_provider(GroqAdapter(
            api_key=config.GROQ_API_KEY_2, 
            model_name=config.GROQ_MODEL_2, 
            provider_name="Groq2"
        ))

    def register_provider(self, provider: IAgentProvider):
        """Plugin Architecture: Memungkinkan pendaftaran LLM Provider baru secara dinamis."""
        name = provider.provider_name.upper()
        self._providers[name] = provider

    def complete(self, prompt: str, system_prompt: str = "You are a helpful assistant.", provider: str = "Groq", model: str = None, temperature: float = 0.2, mock: bool = False, response_format: dict = None) -> str:
        provider_key = provider.upper()
        
        if mock or config.MOCK_MODE:
            return self._mock_completion(provider, model, prompt)
            
        if provider_key not in self._providers:
            log_warning(f"Provider {provider} tidak dikenali/tidak terdaftar. Fallback ke Mock.")
            return self._mock_completion(provider, model, prompt)
            
        active_provider = self._providers[provider_key]
        
        context = {
            "temperature": temperature,
            "response_format": response_format
        }
        
        return active_provider.generate_response(system_prompt, prompt, context)

    def _mock_completion(self, provider: str, model: str, prompt: str) -> str:
        """Simulasi respon jika API Key tidak aktif atau error."""
        return f"[MOCK - {provider} - {model or 'default'}] Respon simulasi terhadap prompt: '{prompt[:100]}...'"

# Global model router instance
model_router = ModelRouter()
