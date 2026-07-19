import sys
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.theme import Theme

# Custom styling theme for the Project Nexus agents
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "danger": "bold red",
    "success": "bold green",
    "planner": "bold blue",
    "research": "bold magenta",
    "developer": "bold yellow",
    "reviewer": "bold green",
    "githubanalyzer": "bold cyan",
})

console = Console(theme=custom_theme)
error_console = Console(stderr=True, theme=custom_theme)

# Callback registry untuk integrasi GUI/Frontend
log_callbacks = []

def add_log_callback(callback):
    """Mendaftarkan fungsi callback untuk menerima log baru."""
    log_callbacks.append(callback)

def _emit_log(level: str, message: str, agent_name: str = None):
    for cb in log_callbacks:
        try:
            cb(level, message, agent_name)
        except Exception:
            pass
            
    # Publish to EventBus (Layer 23 Event Driven Architecture)
    try:
        from services.event_bus import EventBus, NexusEvent
        import config
        
        event_map = {
            "TASK": ("TaskStarted", "INFO", "NORMAL"),
            "AGENT_START": ("AgentThinking", "INFO", "NORMAL"),
            "AGENT_OUTPUT": ("AgentFinished", "INFO", "NORMAL"),
            "EVALUATION": ("TaskCompleted", "SUCCESS", "HIGH"),
            "NEXT_ACTION": ("TaskCompleted", "SUCCESS", "NORMAL"),
            "ERROR": ("TaskFailed", "ERROR", "HIGH")
        }
        
        if level in event_map:
            event_type, status, priority = event_map[level]
            
            # Map agent to active config models dynamically
            model = "N/A"
            if agent_name == "Planner":
                model = config.GROQ_MODEL
            elif agent_name == "Research":
                model = config.KIMI_MODEL
            elif agent_name == "Developer":
                model = config.GROQ_MODEL
            elif agent_name == "Reviewer":
                model = config.KIMI_MODEL
                
            event = NexusEvent(
                event_type=event_type,
                payload={"message": message},
                agent=agent_name or "System",
                model=model,
                status=status,
                priority=priority
            )
            EventBus().publish(event)
    except Exception:
        pass

def log_task(task_title: str):
    """Log the overall task title in a cyan panel."""
    console.print()
    console.print(Panel(f"[bold white]Task:[/bold white] {task_title}", border_style="cyan"))
    _emit_log("TASK", task_title)

def log_agent_header(agent_name: str, model_used: str, reason: str):
    """Log the agent initialization header with model and selection reason."""
    style = agent_name.lower()
    console.print()
    console.print(Panel(
        f"[bold]Model yang digunakan:[/bold] {model_used}\n"
        f"[bold]Alasan pemilihan model:[/bold] {reason}",
        title=f"[bold]{agent_name.upper()} RUNNING[/bold]",
        border_style=style
    ))
    _emit_log("AGENT_START", f"Running agent with model: {model_used}\nSelection Reason: {reason}", agent_name)

def log_agent_output(agent_name: str, output: str):
    """Log the agent's main text or markdown output."""
    style = agent_name.lower()
    console.print(Panel(
        Markdown(output),
        title=f"[bold]{agent_name.upper()} OUTPUT[/bold]",
        border_style=style
    ))
    _emit_log("AGENT_OUTPUT", output, agent_name)

def log_evaluation(evaluation: str):
    """Log the evaluator/reviewer assessment."""
    console.print(Panel(
        Markdown(evaluation),
        title="[bold green]EVALUATION[/bold green]",
        border_style="success"
    ))
    _emit_log("EVALUATION", evaluation)

def log_next_action(next_action: str):
    """Log the final recommendation or next steps."""
    console.print(Panel(
        f"{next_action}",
        title="[bold yellow]NEXT ACTION[/bold yellow]",
        border_style="warning"
    ))
    _emit_log("NEXT_ACTION", next_action)

def log_info(msg: str):
    console.print(f"[info]\[INFO] {msg}[/info]")
    _emit_log("INFO", msg)

def log_warning(msg: str):
    console.print(f"[warning]\[WARNING] {msg}[/warning]")
    _emit_log("WARNING", msg)

def log_error(msg: str):
    error_console.print(f"[danger]\[ERROR] {msg}[/danger]")
    _emit_log("ERROR", msg)
