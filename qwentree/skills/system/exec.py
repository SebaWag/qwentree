"""⚙️ system/exec — Execute system commands and programs."""

from qwentree.core.terminal import terminal


def exec_command(command: str, timeout: int = 30, cwd: str = None) -> dict:
    """Execute a system command.

    Args:
        command: Shell command to execute
        timeout: Timeout in seconds
        cwd: Working directory (default: workspace)
    Returns:
        dict with command output
    """
    result = terminal.run(command, timeout=timeout, cwd=cwd)
    return {
        "success": result["success"],
        "stdout": result["stdout"],
        "stderr": result["stderr"],
        "returncode": result["returncode"],
        "duration": result["duration"],
        "timeout": result["timeout"],
    }


def info() -> dict:
    """Get system information.

    Returns OS, CPU, memory, disk, and Python version.
    """
    import platform
    import shutil

    info = {
        "hostname": platform.node(),
        "os": f"{platform.system()} {platform.release()}",
        "python": platform.python_version(),
        "cpu": platform.processor() or "unknown",
    }

    # Disk usage
    total, used, free = shutil.disk_usage("/home")
    info["disk"] = {
        "total_gb": round(total / (1024**3), 1),
        "used_gb": round(used / (1024**3), 1),
        "free_gb": round(free / (1024**3), 1),
        "used_percent": round(used / total * 100, 1),
    }

    return {"success": True, "system": info}
