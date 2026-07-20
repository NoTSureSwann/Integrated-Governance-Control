import config
from groq import Groq
from ports.agent_port import IAgentProvider
from typing import Dict, Any
from utils.logger import log_warning

class GroqAdapter(IAgentProvider):
    def __init__(self, api_key: str = None, model_name: str = None, provider_name: str = "Groq"):
        self._api_key = api_key or config.GROQ_API_KEY_1
        self._model_name = model_name or config.GROQ_MODEL_1
        self._provider_name = provider_name
        self._client = Groq(api_key=self._api_key) if self._api_key else None

    @property
    def provider_name(self) -> str:
        return self._provider_name
        
    @property
    def model_name(self) -> str:
        return self._model_name

    def generate_response(self, system_prompt: str, user_prompt: str, context: Dict[str, Any] = None) -> str:
        if not self._client:
            log_warning("GROQ_API_KEY tidak ditemukan. Fallback ke Mock.")
            return f"[MOCK - GROQ - {self.model_name}]\nSystem: {system_prompt}\nUser: {user_prompt}"
            
        try:
            # We can optionally pass temperature or json format from context
            temperature = context.get("temperature", 0.2) if context else 0.2
            response_format = context.get("response_format", None) if context else None
            
            kwargs = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": temperature
            }
            if response_format:
                kwargs["response_format"] = response_format
                
            response = self._client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            return f"Error from Groq: {str(e)}"
