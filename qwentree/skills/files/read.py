"""📁 files/read — Read files in various formats."""

from pathlib import Path


def read(file_path: str, max_chars: int = 8000) -> dict:
    """Read a file and return its contents.

    Supports: .txt, .py, .md, .json, .yaml, .csv, .log, .html

    Args:
        file_path: Path to the file
        max_chars: Maximum characters to read (default: 8000)
    Returns:
        dict with keys: content, path, size, extension
    """
    path = Path(file_path).expanduser().resolve()

    if not path.exists():
        return {"success": False, "error": f"File not found: {path}"}

    if not path.is_file():
        return {"success": False, "error": f"Not a file: {path}"}

    try:
        content = path.read_text(encoding="utf-8")
        ext = path.suffix.lower()
        size = path.stat().st_size

        if len(content) > max_chars:
            content = content[:max_chars] + f"\n\n... [truncated {len(content) - max_chars} more chars]"

        return {
            "success": True,
            "content": content,
            "path": str(path),
            "size": size,
            "extension": ext,
            "lines": content.count("\n") + 1,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def read_lines(file_path: str, start: int = 0, end: int = 50) -> dict:
    """Read specific lines from a file.

    Args:
        file_path: Path to the file
        start: Starting line number (0-indexed)
        end: Ending line number
    """
    path = Path(file_path).expanduser().resolve()
    if not path.exists():
        return {"success": False, "error": f"File not found: {path}"}

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        selected = lines[start:end]
        return {
            "success": True,
            "lines": selected,
            "start": start,
            "end": min(end, len(lines)),
            "total_lines": len(lines),
            "content": "\n".join(selected),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
