import argparse
import sys
from orchestrator import NexusOrchestrator
from utils.logger import console, log_error

def main():
    # Print high-quality startup banner
    console.print("""[bold cyan]
=========================================================
               PROJECT NEXUS (v0.1)
        AI Multi-Agent Research Workspace
=========================================================
[/bold cyan]""")

    parser = argparse.ArgumentParser(description="Nexus AI Multi-Agent Workspace Runner")
    parser.add_argument("prompt", type=str, nargs="?", help="Tugas atau pertanyaan riset/pengembangan yang ingin diselesaikan.")
    parser.add_argument("--mock", action="store_true", help="Paksa eksekusi dalam mode simulasi (mock) tanpa memanggil API.")
    args = parser.parse_args()

    # Get prompt interactively if not provided via arguments
    prompt = args.prompt
    if not prompt:
        try:
            prompt = console.input("[bold cyan]Nexus [/bold cyan]>[bold yellow] Masukkan tugas riset/pengembangan: [/bold yellow]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold red]Operasi dibatalkan oleh pengguna.[/bold red]")
            sys.exit(0)

    if not prompt.strip():
        log_error("Tugas tidak boleh kosong!")
        sys.exit(1)

    # Initialize and execute orchestrator
    orchestrator = NexusOrchestrator(mock=args.mock)
    try:
        orchestrator.run_pipeline(prompt)
    except Exception as e:
        log_error(f"Gagal menjalankan pipeline: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
