from typing import Dict, Any, Protocol

class IAgentProvider(Protocol):
    @property
    def provider_name(self) -> str:
        ...
        
    @property
    def model_name(self) -> str:
        ...

    def generate_response(self, system_prompt: str, user_prompt: str, context: Dict[str, Any] = None) -> str:
        ...
