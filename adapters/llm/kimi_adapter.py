import config
from openai import OpenAI
from ports.agent_port import IAgentProvider
from typing import Dict, Any
from utils.logger import log_warning

class KimiAdapter(IAgentProvider):
    def __init__(self, api_key: str = None, model_name: str = None):
        self._api_key = api_key or config.KIMI_API_KEY
        self._model_name = model_name or config.KIMI_MODEL
        self._client = OpenAI(
            api_key=self._api_key,
            base_url="https://api.moonshot.cn/v1",
        ) if self._api_key else None

    @property
    def provider_name(self) -> str:
        return "Kimi"
        
    @property
    def model_name(self) -> str:
        return self._model_name

    def generate_response(self, system_prompt: str, user_prompt: str, context: Dict[str, Any] = None) -> str:
        if not self._client:
            log_warning("KIMI_API_KEY tidak ditemukan. Fallback ke Mock.")
            return f"[MOCK - KIMI - {self.model_name}]\nSystem: {system_prompt}\nUser: {user_prompt}"
            
        try:
            temperature = context.get("temperature", 0.3) if context else 0.3
            
            response = self._client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error from Kimi: {str(e)}"
