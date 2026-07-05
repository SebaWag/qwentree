"""💻 code/analyze — Analyze source code for quality, patterns, and issues."""

import ast
from pathlib import Path


def analyze(file_path: str) -> dict:
    """Analyze a Python source code file.

    Performs static analysis: structure, complexity, issues.

    Args:
        file_path: Path to the Python file
    Returns:
        dict with analysis results
    """
    path = Path(file_path).expanduser().resolve()

    if not path.exists():
        return {"success": False, "error": f"File not found: {path}"}

    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)

        # Count structures
        classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        async_funcs = [n for n in ast.walk(tree) if isinstance(n, ast.AsyncFunctionDef)]
        imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]

        # Find long functions (>30 lines)
        long_funcs = []
        for func in functions:
            if hasattr(func, 'end_lineno') and func.end_lineno:
                lines = func.end_lineno - func.lineno
                if lines > 30:
                    long_funcs.append({
                        "name": func.name,
                        "lines": lines,
                        "line": func.lineno,
                    })

        # Find functions without docstrings
        no_doc = []
        for func in functions:
            docstring = ast.get_docstring(func)
            if not docstring:
                no_doc.append({
                    "name": func.name,
                    "line": func.lineno,
                })

        # Lines of code
        loc = len(source.splitlines())
        blank_lines = sum(1 for line in source.splitlines() if not line.strip())

        return {
            "success": True,
            "file": str(path),
            "summary": {
                "lines_of_code": loc,
                "blank_lines": blank_lines,
                "classes": len(classes),
                "functions": len(functions) + len(async_funcs),
                "async_functions": len(async_funcs),
                "imports": len(imports),
            },
            "issues": {
                "long_functions": long_funcs,
                "no_docstrings": no_doc,
            },
            "total_functions_analyzed": len(functions),
        }
    except SyntaxError as e:
        return {"success": False, "error": f"Syntax error: {e}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
