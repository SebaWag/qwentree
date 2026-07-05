"""💻 code/run — Execute Python code in a sandbox."""

from qwentree.core.terminal import terminal


def run(code: str, timeout: int = 30) -> dict:
    """Execute Python code in a sandboxed subprocess.

    Args:
        code: Python code to execute
        timeout: Timeout in seconds
    Returns:
        dict with stdout, stderr, success status
    """
    result = terminal.run_python(code, timeout=timeout)
    return {
        "success": result["success"],
        "stdout": result["stdout"],
        "stderr": result["stderr"],
        "returncode": result["returncode"],
        "duration": result["duration"],
        "timeout": result["timeout"],
    }


def run_file(script_path: str, timeout: int = 60) -> dict:
    """Execute a Python script file.

    Args:
        script_path: Path to the Python script
        timeout: Timeout in seconds
    """
    result = terminal.run_script(script_path, timeout=timeout)
    return {
        "success": result["success"],
        "stdout": result["stdout"],
        "stderr": result["stderr"],
        "returncode": result["returncode"],
    }


def run_shell(command: str, timeout: int = 30) -> dict:
    """Execute a shell command.

    Args:
        command: Shell command to execute
        timeout: Timeout in seconds
    """
    result = terminal.run(command, timeout=timeout)
    return {
        "success": result["success"],
        "stdout": result["stdout"],
        "stderr": result["stderr"],
        "returncode": result["returncode"],
        "duration": result["duration"],
    }
