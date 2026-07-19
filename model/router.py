import os
import requests
from openai import OpenAI
from groq import Groq
import config
from utils.logger import log_info, log_warning

class ModelRouter:
    """
    Layer 6: MODEL ROUTER
    Arahkan request ke LLM Provider yang tepat (Groq, Kimi, OpenAI, Ollama, Anthropic, Gemini, Mistral)
    berdasarkan kemampuan model dan ketersediaan API key.
    """
    def __init__(self):
        # Cache clients to avoid recreation
        self._groq_client = None
        self._openai_client = None
        self._kimi_client = None

    def get_groq_client(self):
        if not self._groq_client and config.GROQ_API_KEY:
            self._groq_client = Groq(api_key=config.GROQ_API_KEY)
        return self._groq_client

    def get_openai_client(self):
        if not self._openai_client and config.OPENAI_API_KEY:
            self._openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
        return self._openai_client

    def get_kimi_client(self):
        if not self._kimi_client and config.KIMI_API_KEY:
            self._kimi_client = OpenAI(
                api_key=config.KIMI_API_KEY,
                base_url=config.KIMI_BASE_URL
            )
        return self._kimi_client

    def complete(self, prompt: str, system_prompt: str = "You are a helpful assistant.", provider: str = "Groq", model: str = None, temperature: float = 0.2, mock: bool = False, response_format: dict = None) -> str:
        """
        Melakukan penyelesaian chat (chat completion) secara terpadu.
        """
        # Determine provider and model fallback
        provider = provider.upper()
        if mock or config.MOCK_MODE:
            return self._mock_completion(provider, model, prompt)

        try:
            if provider == "GROQ":
                client = self.get_groq_client()
                if not client:
                    log_warning("GROQ_API_KEY tidak ditemukan. Fallback ke Mock.")
                    return self._mock_completion(provider, model, prompt)
                
                model_name = model or config.GROQ_MODEL
                
                kwargs = {
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": temperature
                }
                if response_format:
                    kwargs["response_format"] = response_format
                    
                completion = client.chat.completions.create(**kwargs)
                return completion.choices[0].message.content

            elif provider == "KIMI":
                client = self.get_kimi_client()
                if not client:
                    log_warning("KIMI_API_KEY tidak ditemukan. Fallback ke Mock.")
                    return self._mock_completion(provider, model, prompt)

                model_name = model or config.KIMI_MODEL
                kwargs = {
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": temperature
                }
                if response_format:
                    kwargs["response_format"] = response_format
                    
                completion = client.chat.completions.create(**kwargs)
                return completion.choices[0].message.content

            elif provider == "OPENAI":
                client = self.get_openai_client()
                if not client:
                    log_warning("OPENAI_API_KEY tidak ditemukan. Fallback ke Mock.")
                    return self._mock_completion(provider, model, prompt)

                model_name = model or config.OPENAI_MODEL
                kwargs = {
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": temperature
                }
                if response_format:
                    kwargs["response_format"] = response_format
                    
                completion = client.chat.completions.create(**kwargs)
                return completion.choices[0].message.content

            elif provider == "OLLAMA":
                # Ollama runs locally, we can use local OpenAI client wrapper
                ollama_client = OpenAI(
                    api_key="ollama",
                    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
                )
                model_name = model or "llama3"
                completion = ollama_client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature
                )
                return completion.choices[0].message.content

            elif provider in ("ANTHROPIC", "GEMINI", "MISTRAL"):
                # Scaffolded integration, fall back to mock for now
                log_info(f"Integrasi {provider} belum di-setup penuh di Phase 2. Menjalankan Mock.")
                return self._mock_completion(provider, model, prompt)

            else:
                log_warning(f"Provider {provider} tidak dikenali. Fallback ke Mock.")
                return self._mock_completion(provider, model, prompt)

        except Exception as e:
            log_warning(f"Error pada ModelRouter untuk {provider} ({model}): {e}. Fallback ke Mock.")
            return self._mock_completion(provider, model, prompt)

    def _mock_completion(self, provider: str, model: str, prompt: str) -> str:
        """Simulasi respon jika API Key tidak aktif atau error."""
        return f"[MOCK - {provider} - {model or 'default'}] Respon simulasi terhadap prompt: '{prompt[:100]}...'"

# Global model router instance
model_router = ModelRouter()
