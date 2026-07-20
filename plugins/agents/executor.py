import os
import re
import subprocess
from plugins.agents.base import BaseAgent
from utils.logger import log_info, log_error

class ExecutorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Executor",
            model_provider="Local",
            model_name="Subprocess",
            default_reason="Agen eksekutor bertugas menjalankan skrip atau kode yang dihasilkan oleh Developer Agent secara aman."
        )

    def get_selection_reason(self, task_type: str = "") -> str:
        return self.default_reason

    def run(self, context: dict, user_prompt: str, mock: bool = False) -> str:
        developer_output = context.get("Developer", "")
        
        # Ekstrak blok kode python
        code = self._extract_python_code(developer_output)
        if not code:
            return "No Python code found in the Developer's output to execute."
            
        # Simpan ke sandbox
        sandbox_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "workspace", "sandbox"))
        os.makedirs(sandbox_dir, exist_ok=True)
        temp_file = os.path.join(sandbox_dir, "temp.py")
        
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(code)
            
            # Jika dalam mode mock, kita tidak perlu menjalankan kodenya, atau jalankan juga tidak apa-apa jika aman
            # Tapi sebaiknya eksekusi betulan untuk simulasi Executor
            if mock:
                return "Mock Mode: Code execution skipped.\n\nCode to execute:\n```python\n" + code + "\n```"

            # Jalankan kode dengan batas waktu
            log_info(f"Executing {temp_file}...")
            result = subprocess.run(
                ["python", temp_file],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=sandbox_dir
            )
            
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            
            output = "## Execution Output\n\n"
            output += f"**Exit Code:** `{result.returncode}`\n\n"
            
            if stdout:
                output += f"### Standard Output (STDOUT)\n```text\n{stdout}\n```\n"
            if stderr:
                output += f"### Standard Error (STDERR)\n```text\n{stderr}\n```\n"
                
            return output
            
        except subprocess.TimeoutExpired:
            return "## Execution Error\n\nTask timed out after 30 seconds."
        except Exception as e:
            log_error(f"Execution Error: {str(e)}")
            return f"## Execution Error\n\nException occurred: {str(e)}"
            
    def _run_mock(self, user_prompt: str) -> str:
        # Override BaseAgent mock behavior since we have custom mock logic in run()
        return "Mock Mode execution."

    def _extract_python_code(self, text: str) -> str:
        # Mencari string di dalam ```python ... ```
        pattern = r"```python(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        if matches:
            return "\n".join(matches)
        
        # Jika tidak ada label python, cari blok kode biasa
        pattern_any = r"```(.*?)```"
        matches_any = re.findall(pattern_any, text, re.DOTALL)
        if matches_any:
            return "\n".join(matches_any)
            
        return ""
