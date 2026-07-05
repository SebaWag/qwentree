"""📁 files/write — Create and write files."""

from pathlib import Path


def write(file_path: str, content: str, mode: str = "w") -> dict:
    """Write content to a file.

    Args:
        file_path: Path where to write the file
        content: Content to write
        mode: 'w' to overwrite, 'a' to append
    Returns:
        dict with success status and file info
    """
    path = Path(file_path).expanduser().resolve()

    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        if mode == "a":
            with open(path, "a", encoding="utf-8") as f:
                f.write(content)
        else:
            path.write_text(content, encoding="utf-8")

        stat = path.stat()
        return {
            "success": True,
            "path": str(path),
            "size": stat.st_size,
            "mode": mode,
            "message": f"✅ File written: {path} ({stat.st_size} bytes)",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def append(file_path: str, content: str) -> dict:
    """Append content to an existing file."""
    return write(file_path, content, mode="a")
