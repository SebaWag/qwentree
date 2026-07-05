"""📁 files/search — Search files by name, content, or pattern."""

from pathlib import Path
import fnmatch


def search(pattern: str, search_path: str = "~", max_results: int = 30) -> dict:
    """Search for files matching a glob pattern.

    Args:
        pattern: Glob pattern (e.g., '*.py', '*.md', 'config*')
        search_path: Directory to search in (default: home)
        max_results: Maximum results to return
    Returns:
        dict with list of matching files
    """
    base = Path(search_path).expanduser().resolve()

    if not base.exists():
        return {"success": False, "error": f"Path not found: {base}"}

    results = []
    try:
        for path in base.rglob(pattern):
            if len(results) >= max_results:
                break
            try:
                stat = path.stat()
                results.append({
                    "name": path.name,
                    "path": str(path),
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "extension": path.suffix,
                })
            except (PermissionError, OSError):
                continue

        return {
            "success": True,
            "pattern": pattern,
            "search_path": str(base),
            "total": len(results),
            "results": results,
            "truncated": len(results) >= max_results,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def find_by_content(query: str, search_path: str = "~",
                    file_pattern: str = "*",
                    max_results: int = 10) -> dict:
    """Search for files containing specific text.

    Args:
        query: Text to search for
        search_path: Directory to search in
        file_pattern: File pattern to filter by
        max_results: Maximum files to return
    """
    base = Path(search_path).expanduser().resolve()
    results = []

    try:
        for path in base.rglob(file_pattern):
            if len(results) >= max_results:
                break
            if not path.is_file():
                continue
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
                if query.lower() in content.lower():
                    results.append({
                        "name": path.name,
                        "path": str(path),
                        "extension": path.suffix,
                    })
            except (PermissionError, OSError):
                continue

        return {
            "success": True,
            "query": query,
            "search_path": str(base),
            "total": len(results),
            "results": results,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
