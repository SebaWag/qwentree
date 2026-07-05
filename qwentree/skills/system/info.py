"""⚙️ system/info — Get system information."""

import platform
import shutil
import os
import datetime


def info() -> dict:
    """Get comprehensive system information.

    Returns OS, CPU, memory, disk, processes, and environment details.
    """
    # CPU info
    cpu_info = {}
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if "model name" in line:
                    cpu_info["model"] = line.split(":")[1].strip()
                    break
    except FileNotFoundError:
        cpu_info["model"] = platform.processor() or "unknown"

    try:
        cpu_count = os.cpu_count() or 0
    except:
        cpu_count = 0

    # Memory
    mem = {}
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if "MemTotal" in line:
                    mem["total_gb"] = round(int(line.split()[1]) / 1024 / 1024, 1)
                elif "MemAvailable" in line:
                    mem["available_gb"] = round(int(line.split()[1]) / 1024 / 1024, 1)
    except FileNotFoundError:
        mem = {"total_gb": "unknown", "available_gb": "unknown"}

    # Disk
    disk = {}
    try:
        usage = shutil.disk_usage("/home")
        disk = {
            "total_gb": round(usage.total / (1024**3), 1),
            "used_gb": round(usage.used / (1024**3), 1),
            "free_gb": round(usage.free / (1024**3), 1),
            "used_percent": round(usage.used / usage.total * 100, 1),
        }
    except:
        disk = {"error": "unavailable"}

    # Uptime
    uptime = "unknown"
    try:
        with open("/proc/uptime") as f:
            seconds = float(f.read().split()[0])
            uptime = str(datetime.timedelta(seconds=int(seconds)))
    except:
        pass

    return {
        "success": True,
        "system": {
            "hostname": platform.node(),
            "os": f"{platform.system()} {platform.release()}",
            "kernel": platform.version(),
            "architecture": platform.machine(),
        },
        "cpu": {
            "model": cpu_info.get("model", "unknown"),
            "cores": cpu_count,
        },
        "memory": mem,
        "disk": disk,
        "uptime": uptime,
        "python": platform.python_version(),
        "time": datetime.datetime.now().isoformat(),
    }
