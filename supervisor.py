import json
from model.router import model_router
import config
from utils.logger import log_warning, log_info, console
from rich.panel import Panel
from agents.base import BaseAgent

class SupervisorEngine:
    """
    Layer 2: SUPERVISOR
    Menerima request, menentukan prioritas, memilih workflow/agent (routing),
    dan mendelegasikan tugas tanpa menghasilkan jawaban teknis langsung.
    """
    def __init__(self, mock: bool = False):
        self.mock = mock
        self.model_name = config.GROQ_MODEL
        
    def route_request(self, user_prompt: str) -> dict:
        """
        Menganalisis request pengguna dan menentukan route/prioritas.
        Returns a dict: {"route": "STANDARD" | "GITHUB_ANALYZER", "priority": "HIGH", "github_url": "..."}
        """
        system_prompt = (
            "Anda adalah Supervisor di Project Nexus (Layer 2).\n"
            "Tugas Anda adalah menerima request pengguna dan menentukan 'route' (jalur) eksekusi.\n"
            "Jika pengguna meminta untuk menganalisis, membaca, atau mengekstrak knowledge dari sebuah repository GitHub (menyertakan link github.com), "
            "balas dengan route 'GITHUB_ANALYZER' dan cantumkan 'github_url'.\n"
            "Jika pengguna meminta tugas software engineering, coding, atau riset umum, balas dengan 'STANDARD'.\n"
            "Output WAJIB berupa JSON murni dengan skema: {\"route\": \"...\", \"priority\": \"HIGH|NORMAL|LOW\", \"github_url\": \"...\" (opsional, jika ada)}"
        ) + BaseAgent.get_constitution()
        
        try:
            # Use ModelRouter with response_format
            response_text = model_router.complete(
                prompt=user_prompt,
                system_prompt=system_prompt,
                provider="Groq",
                model=self.model_name,
                temperature=0.1,
                mock=self.mock,
                response_format={"type": "json_object"}
            )
            route_data = json.loads(response_text)
            self._log_routing(route_data)
            return route_data
        except Exception as e:
            log_warning(f"Supervisor API Error: {e}. Fallback to mock routing.")
            return self._mock_route(user_prompt)
            
    def _mock_route(self, user_prompt: str) -> dict:
        route_data = {"route": "STANDARD", "priority": "NORMAL"}
        if "github.com" in user_prompt.lower():
            words = user_prompt.split()
            url = next((w for w in words if "github.com" in w), None)
            route_data = {"route": "GITHUB_ANALYZER", "priority": "HIGH", "github_url": url}
        self._log_routing(route_data)
        return route_data
        
    def _log_routing(self, route_data: dict):
        console.print()
        console.print(Panel(
            f"[bold cyan]Route Terpilih:[/bold cyan] {route_data.get('route', 'STANDARD')}\n"
            f"[bold cyan]Prioritas:[/bold cyan] {route_data.get('priority', 'NORMAL')}",
            title="[bold yellow]SUPERVISOR ROUTING[/bold yellow]",
            border_style="yellow"
        ))
