"""files/tree -- Display directory tree structure."""

from pathlib import Path


def tree(directory: str = ".", max_depth: int = 3, show_hidden: bool = False) -> dict:
    """Display the directory tree structure."""
    base = Path(directory).expanduser().resolve()

    if not base.exists():
        return {"success": False, "error": "Directory not found: " + str(base)}

    if not base.is_dir():
        return {"success": False, "error": "Not a directory: " + str(base)}

    lines = []
    structure = {"name": base.name, "type": "directory", "children": []}

    def _walk(path, depth, parent_dict):
        if depth > max_depth:
            return
        prefix = "  " * depth + ("-- " if depth > 0 else "")
        try:
            entries = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name))
        except PermissionError:
            return
        for entry in entries:
            if entry.name.startswith(".") and not show_hidden:
                continue
            is_dir = entry.is_dir()
            name = entry.name + ("/" if is_dir else "")
            lines.append(prefix + name)
            child = {"name": entry.name, "type": "directory" if is_dir else "file", "path": str(entry)}
            if is_dir:
                child["children"] = []
            parent_dict["children"].append(child)
            if is_dir:
                _walk(entry, depth + 1, child)

    _walk(base, 0, structure)

    return {
        "success": True,
        "directory": str(base),
        "max_depth": max_depth,
        "tree_text": "\n".join(lines),
        "structure": structure,
    }
