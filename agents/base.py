from abc import ABC, abstractmethod

class BaseAgent(ABC):
    def __init__(self, name: str, model_provider: str, model_name: str, default_reason: str):
        self.name = name
        self.model_provider = model_provider
        self.model_name = model_name
        self.default_reason = default_reason

    @abstractmethod
    def run(self, context: dict, user_prompt: str, mock: bool = False) -> str:
        """
        Execute the agent's main logic.
        
        :param context: Dict containing outputs from other agents in the workflow.
        :param user_prompt: The original prompt or goal from the user.
        :param mock: If True, execute in mock mode (bypassing API calls).
        :return: Text result from the agent.
        """
        pass
        
    @abstractmethod
    def get_selection_reason(self, task_type: str = "") -> str:
        """Return the rationale for using this agent's model for the task."""
        return self.default_reason

    def execute_with_telemetry(self, context: dict, user_prompt: str, mock: bool = False) -> str:
        """
        Layer 16: OBSERVABILITY ENGINE
        Wrapper method untuk mengukur performa agen dan sistem, 
        lalu menyimpan telemetry sebelum mengembalikan output asli.
        """
        import time
        import psutil
        from telemetry import TelemetryClient
        
        telemetry = TelemetryClient()
        
        # Capture hardware states before
        cpu_before = psutil.cpu_percent(interval=None)
        ram_before = psutil.virtual_memory().percent
        
        start_time = time.time()
        
        # Eksekusi agen aktual
        output = self.run(context, user_prompt, mock=mock)
        
        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000.0
        
        # Capture hardware states after
        cpu_after = psutil.cpu_percent(interval=None)
        ram_after = psutil.virtual_memory().percent
        
        # Average or max spike
        cpu_usage = max(cpu_before, cpu_after)
        ram_usage = max(ram_before, ram_after)
        
        # (GPU tracking logic can be added here optionally if GPUtil is available)
        gpu_usage = 0.0
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_usage = gpus[0].load * 100
        except Exception:
            pass
            
        # Simulasikan perhitungan token atau latency
        # Di implementasi live, ini bisa didapat dari metadata API
        api_latency = response_time_ms * 0.9 # Asumsi 90% waktu adalah network latency
        token_usage = len(output.split()) * 1.5 # Estimasi kasar
        
        # Catat metrik
        telemetry.log_event(
            agent_name=self.name,
            model_name=self.model_name,
            task_name="Agent Execution",
            response_time_ms=response_time_ms,
            token_usage=int(token_usage),
            cpu_usage=cpu_usage,
            ram_usage=ram_usage,
            gpu_usage=gpu_usage,
            api_latency=api_latency,
            success_rate=1.0,
            error_count=0
        )
        
        return output

    @classmethod
    def get_constitution(cls) -> str:
        """
        Mengembalikan teks Konstitusi Proyek untuk disisipkan ke dalam System Prompt agen.
        """
        return (
            "\n\n==========================================================\n"
            "PROJECT CONSTITUTION (WAJIB DIPATUHI SECARA MUTLAK):\n"
            "1. Human First: Utamakan manusia di atas segalanya.\n"
            "2. Safety Before Automation: Keamanan sebelum otomatisasi tindakan.\n"
            "3. Evidence Before Conclusion: Pisahkan fakta empiris dari asumsi/opini.\n"
            "4. Explain Every Decision: Berikan penjelasan logis atas setiap keputusan Anda.\n"
            "5. Modular By Default: Rancang arsitektur/kode secara modular & independen.\n"
            "6. Reproducible Research: Dokumentasikan riset & eksperimen secara menyeluruh.\n"
            "7. Never Assume Without Evidence: Klasifikasikan data secara eksplisit menjadi:\n"
            "   [FACT] / [ASSUMPTION] / [HYPOTHESIS] / [REFERENCE] / [EXPERIMENT].\n"
            "8. Learn Only From Authorized Sources: Hanya belajar dari sumber data publik resmi & feedback sah.\n"
            "9. Preserve User Control: Minta otorisasi manual sebelum melakukan aksi kritis.\n"
            "10. Improve Continuously: Gunakan hasil review & kritik untuk meningkatkan performa.\n"
            "==========================================================\n"
        )
