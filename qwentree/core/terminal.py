"""Terminal Sandbox -- Execute shell commands and code safely."""

import asyncio
import subprocess
import sys
import os
import tempfile
import shlex
from typing import Optional, Tuple
from datetime import datetime


class TerminalSandbox:
    """Sandboxed terminal execution with logging and timeouts."""

    MAX_OUTPUT_LENGTH = 50000
    DEFAULT_TIMEOUT = 30
    MAX_TIMEOUT = 300

    def __init__(self, workspace_dir: str = ""):
        if not workspace_dir:
            workspace_dir = tempfile.mkdtemp(prefix="qwentree_ws_")
        self.workspace_dir = workspace_dir
        os.makedirs(workspace_dir, exist_ok=True)
        self._history: list[dict] = []

    def run(self, command: str,
            timeout: Optional[int] = None,
            cwd: Optional[str] = None,
            capture_output: bool = True) -> dict:
        """Execute a shell command in the sandbox."""
        timeout = min(timeout or self.DEFAULT_TIMEOUT, self.MAX_TIMEOUT)
        cwd = cwd or self.workspace_dir
        start = datetime.now()

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=capture_output,
                text=True,
                timeout=timeout,
                cwd=cwd,
                executable="/bin/bash",
            )

            stdout = result.stdout or ""
            stderr = result.stderr or ""

            if len(stdout) > self.MAX_OUTPUT_LENGTH:
                stdout = stdout[:self.MAX_OUTPUT_LENGTH] + \
                         "\n... [truncated {} chars]".format(len(stdout) - self.MAX_OUTPUT_LENGTH)

            entry = {
                "success": result.returncode == 0,
                "stdout": stdout,
                "stderr": stderr,
                "returncode": result.returncode,
                "duration": (datetime.now() - start).total_seconds(),
                "command": command,
                "timeout": False,
            }

        except subprocess.TimeoutExpired:
            entry = {
                "success": False,
                "stdout": "",
                "stderr": "Command timed out after {}s".format(timeout),
                "returncode": -1,
                "duration": timeout,
                "command": command,
                "timeout": True,
            }
        except Exception as e:
            entry = {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1,
                "duration": (datetime.now() - start).total_seconds(),
                "command": command,
                "timeout": False,
            }

        self._history.append(entry)
        return entry

    async def run_async(self, command: str, **kwargs) -> dict:
        """Async version of run()."""
        return await asyncio.to_thread(self.run, command, **kwargs)

    def run_python(self, code: str, timeout: int = 30) -> dict:
        """Execute Python code in a subprocess."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", dir=self.workspace_dir, delete=False
        ) as f:
            f.write(code)
            script_path = f.name

        try:
            result = self.run("python3 {}".format(script_path), timeout=timeout)
            return result
        finally:
            try:
                os.unlink(script_path)
            except OSError:
                pass

    def run_script(self, script_path: str, timeout: int = 60) -> dict:
        """Execute a script file."""
        if not os.path.exists(script_path):
            return {
                "success": False,
                "stdout": "",
                "stderr": "Script not found: {}".format(script_path),
                "returncode": -1,
                "duration": 0,
                "command": "run {}".format(script_path),
                "timeout": False,
            }
        return self.run("python3 {}".format(shlex.quote(script_path)), timeout=timeout)

    def get_history(self, last: int = 10) -> list[dict]:
        """Get last N command executions."""
        return self._history[-last:]

    def clear_history(self):
        """Clear execution history."""
        self._history = []

    @property
    def summary(self) -> dict:
        """Get sandbox usage summary."""
        total = len(self._history)
        successes = sum(1 for h in self._history if h["success"])
        return {
            "total_commands": total,
            "successful": successes,
            "failed": total - successes,
            "avg_duration": sum(h["duration"] for h in self._history) / max(total, 1),
            "workspace": self.workspace_dir,
        }


terminal = TerminalSandbox()
