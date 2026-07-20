import os
import json
import datetime
import config
from plugins.agents.planner import PlannerAgent
from plugins.agents.research import ResearchAgent
from plugins.agents.developer import DeveloperAgent
from plugins.agents.executor import ExecutorAgent
from plugins.agents.reviewer import ReviewerAgent
from supervisor import SupervisorEngine
from supervisor import SupervisorEngine
from connectors.github_analyzer import GitHubAnalyzer
from plugins.plugin_manager import PluginManager
import utils.logger as log

class NexusOrchestrator:
    def __init__(self, mock: bool = False):
        self.mock = mock
        self.plugin_manager = PluginManager()
        self.plugin_manager.load_plugins()
        
        self.planner = self.plugin_manager.get_agent("PlannerAgent")
        self.research = self.plugin_manager.get_agent("ResearchAgent")
        self.developer = self.plugin_manager.get_agent("DeveloperAgent")
        
        # Inisialisasi ExecutorAgent secara manual jika belum didaftarkan di manager
        self.executor = ExecutorAgent()
        
        self.reviewer = self.plugin_manager.get_agent("ReviewerAgent")
        self.supervisor = SupervisorEngine(mock=mock)
        self.github_analyzer = GitHubAnalyzer(mock=mock)

    def run_pipeline(self, user_prompt: str) -> dict:
        """
        Runs the sequential multi-agent research and development workspace workflow.
        """
        from services.hook_manager import nexus_hook_manager
        
        # Lifecycle: before_task
        task_ctx = nexus_hook_manager.execute_hooks("before_task", {"user_prompt": user_prompt})
        user_prompt = task_ctx.get("user_prompt", user_prompt)

        # Validate configuration if we are not forcing mock mode
        if not self.mock:
            errors = config.validate_config()
            if errors:
                log.log_warning("Konfigurasi API tidak lengkap:")
                for err in errors:
                    log.log_warning(f" - {err}")
                log.log_warning("Beralih secara otomatis ke mode MOCK (simulasi).")
                self.mock = True

        log.log_task(user_prompt)

        context = {}
        history = []

        # 0. SUPERVISOR STEP (Layer 2)
        with log.console.status("[bold yellow]Supervisor sedang menganalisis request (Routing)...", spinner="dots"):
            route_data = self.supervisor.route_request(user_prompt)
            
        route_type = route_data.get("route", "STANDARD")
        
        # Eksekusi Layer 17 jika diminta oleh Supervisor
        if route_type == "GITHUB_ANALYZER":
            github_url = route_data.get("github_url")
            if not github_url:
                words = user_prompt.split()
                github_url = next((w for w in words if "github.com" in w), "Tidak diketahui")
            
            with log.console.status(f"[bold blue]Menghubungi Open Knowledge Connector untuk {github_url}...", spinner="dots"):
                analyzer_output = self.github_analyzer.analyze_repository(github_url)
                
            context["GitHubAnalyzer"] = analyzer_output
            log.log_agent_output("GitHubAnalyzer", analyzer_output)
            history.append({
                "agent": "GitHubAnalyzer",
                "provider": "Connector",
                "model": "Layer 17",
                "reason": "Permintaan pengguna melibatkan analisis data publik (GitHub).",
                "output": analyzer_output
            })
            
            # Memperkaya prompt untuk Planner agar menggunakan data repository
            user_prompt = f"Berdasarkan hasil ekstrak repositori dari {github_url}, selesaikan tugas berikut:\n\nUser Input: {user_prompt}\n\nHasil Analisis:\n{analyzer_output}"

        # 1. PLANNER STEP (Groq)
        planner_reason = self.planner.get_selection_reason()
        log.log_agent_header(self.planner.name, self.planner.model_name, planner_reason)
        
        # Lifecycle: before_model_call
        nexus_hook_manager.execute_hooks("before_model_call", {"agent": self.planner.name, "model": self.planner.model_name})
        
        with log.console.status("[bold blue]Planner sedang menganalisis dan membagi tugas...", spinner="dots"):
            planner_output = self.planner.execute_with_telemetry(context, user_prompt, mock=self.mock)
            
        # Lifecycle: after_model_call
        model_ctx = nexus_hook_manager.execute_hooks("after_model_call", {"agent": self.planner.name, "model": self.planner.model_name, "output": planner_output})
        planner_output = model_ctx.get("output", planner_output)
            
        context[self.planner.name] = planner_output
        log.log_agent_output(self.planner.name, planner_output)
        history.append({
            "agent": self.planner.name,
            "provider": self.planner.model_provider,
            "model": self.planner.model_name,
            "reason": planner_reason,
            "output": planner_output
        })

        # 2. RESEARCH STEP (Kimi)
        research_reason = self.research.get_selection_reason()
        log.log_agent_header(self.research.name, self.research.model_name, research_reason)
        
        # Lifecycle: before_model_call
        nexus_hook_manager.execute_hooks("before_model_call", {"agent": self.research.name, "model": self.research.model_name})
        
        with log.console.status("[bold magenta]Research sedang menyusun landasan teori...", spinner="dots"):
            research_output = self.research.execute_with_telemetry(context, user_prompt, mock=self.mock)
            
        # Lifecycle: after_model_call
        model_ctx = nexus_hook_manager.execute_hooks("after_model_call", {"agent": self.research.name, "model": self.research.model_name, "output": research_output})
        research_output = model_ctx.get("output", research_output)
            
        context[self.research.name] = research_output
        log.log_agent_output(self.research.name, research_output)
        history.append({
            "agent": self.research.name,
            "provider": self.research.model_provider,
            "model": self.research.model_name,
            "reason": research_reason,
            "output": research_output
        })

        # 3. DEVELOPER STEP (Groq)
        developer_reason = self.developer.get_selection_reason()
        log.log_agent_header(self.developer.name, self.developer.model_name, developer_reason)
        
        # Lifecycle: before_model_call
        nexus_hook_manager.execute_hooks("before_model_call", {"agent": self.developer.name, "model": self.developer.model_name})
        
        with log.console.status("[bold yellow]Developer sedang menulis kode program...", spinner="dots"):
            developer_output = self.developer.execute_with_telemetry(context, user_prompt, mock=self.mock)
            
        # Lifecycle: after_model_call
        model_ctx = nexus_hook_manager.execute_hooks("after_model_call", {"agent": self.developer.name, "model": self.developer.model_name, "output": developer_output})
        developer_output = model_ctx.get("output", developer_output)
            
        context[self.developer.name] = developer_output
        log.log_agent_output(self.developer.name, developer_output)
        history.append({
            "agent": self.developer.name,
            "provider": self.developer.model_provider,
            "model": self.developer.model_name,
            "reason": developer_reason,
            "output": developer_output
        })

        # 4. EXECUTOR STEP (Subprocess)
        executor_reason = self.executor.get_selection_reason()
        log.log_agent_header(self.executor.name, self.executor.model_name, executor_reason)
        
        # Lifecycle: before_model_call
        nexus_hook_manager.execute_hooks("before_model_call", {"agent": self.executor.name, "model": self.executor.model_name})
        
        with log.console.status("[bold cyan]Executor sedang menjalankan kode dari Developer...", spinner="dots"):
            executor_output = self.executor.execute_with_telemetry(context, user_prompt, mock=self.mock)
            
        # Lifecycle: after_model_call
        model_ctx = nexus_hook_manager.execute_hooks("after_model_call", {"agent": self.executor.name, "model": self.executor.model_name, "output": executor_output})
        executor_output = model_ctx.get("output", executor_output)
            
        context[self.executor.name] = executor_output
        log.log_agent_output(self.executor.name, executor_output)
        history.append({
            "agent": self.executor.name,
            "provider": self.executor.model_provider,
            "model": self.executor.model_name,
            "reason": executor_reason,
            "output": executor_output
        })

        # 5. REVIEWER STEP (Kimi)
        reviewer_reason = self.reviewer.get_selection_reason()
        log.log_agent_header(self.reviewer.name, self.reviewer.model_name, reviewer_reason)
        
        # Lifecycle: before_model_call
        nexus_hook_manager.execute_hooks("before_model_call", {"agent": self.reviewer.name, "model": self.reviewer.model_name})
        
        with log.console.status("[bold green]Reviewer sedang mengevaluasi kualitas, logika, dan hasil eksekusi...", spinner="dots"):
            # Gabungkan hasil eksekusi ke prompt pengguna untuk reviewer
            reviewer_prompt = f"{user_prompt}\n\n[Hasil Eksekusi Kode]\n{executor_output}"
            reviewer_output = self.reviewer.execute_with_telemetry(context, reviewer_prompt, mock=self.mock)
            
        # Lifecycle: after_model_call
        model_ctx = nexus_hook_manager.execute_hooks("after_model_call", {"agent": self.reviewer.name, "model": self.reviewer.model_name, "output": reviewer_output})
        reviewer_output = model_ctx.get("output", reviewer_output)
            
        context[self.reviewer.name] = reviewer_output
        log.log_agent_output(self.reviewer.name, reviewer_output)
        history.append({
            "agent": self.reviewer.name,
            "provider": self.reviewer.model_provider,
            "model": self.reviewer.model_name,
            "reason": reviewer_reason,
            "output": reviewer_output
        })

        # Summary Outputs
        evaluation = reviewer_output
        
        # Generate simple clean next actions from Reviewer output
        next_action = (
            "1. Tinjau dan salin kode/analisis dari Developer Agent.\n"
            "2. Jalankan penyesuaian/integrasi lokal sesuai kritik dari Reviewer Agent.\n"
            "3. Lakukan deploy atau kembangkan fungsionalitas tambahan."
        )
        
        log.log_evaluation(evaluation)
        log.log_next_action(next_action)

        result = {
            "timestamp": datetime.datetime.now().isoformat(),
            "task": user_prompt,
            "mock_mode": self.mock,
            "history": history,
            "evaluation": evaluation,
            "next_action": next_action
        }

        # Lifecycle: after_output
        res_ctx = nexus_hook_manager.execute_hooks("after_output", {"result": result})
        result = res_ctx.get("result", result)

        self.save_experiment(result)
        return result

    def save_experiment(self, result: dict):
        """Saves the experiment result to JSON and Markdown reports."""
        os.makedirs("experiments", exist_ok=True)
        timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save JSON file for programmatic analysis
        json_path = f"experiments/run_{timestamp_str}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
            
        # Save Markdown report for human reading
        md_path = f"experiments/run_{timestamp_str}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# Laporan Eksperimen Nexus\n\n")
            f.write(f"- **Task**: {result['task']}\n")
            f.write(f"- **Waktu**: {result['timestamp']}\n")
            f.write(f"- **Mode Simulasi (Mock)**: {result['mock_mode']}\n\n")
            f.write("---\n\n")
            
            for step in result['history']:
                f.write(f"## Agen: {step['agent']}\n")
                f.write(f"- **Model**: {step['provider']} ({step['model']})\n")
                f.write(f"- **Alasan Pemilihan**: {step['reason']}\n\n")
                f.write("### Output:\n")
                f.write(f"{step['output']}\n\n")
                f.write("---\n\n")
                
            f.write(f"## Evaluasi Akhir\n\n{result['evaluation']}\n\n")
            f.write(f"## Next Action\n\n{result['next_action']}\n")
            
        log.log_info(f"Laporan eksperimen disimpan di: [Laporan Markdown](file:///{os.path.abspath(md_path)}) dan [Laporan JSON](file:///{os.path.abspath(json_path)})")
