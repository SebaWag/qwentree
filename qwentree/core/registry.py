"""Skill Registry — Auto-discovers and registers all skills from the tree.

Scans the skills/ directory tree and automatically registers
every callable function as a skill in the SkillTree.
"""

import importlib
import inspect
import pkgutil
from pathlib import Path
from typing import Callable, Optional

from qwentree.tree import skill_tree


def auto_register_skills():
    """Scan all skill modules and register their functions."""
    skills_pkg = "qwentree.skills"
    _scan_package(skills_pkg, skills_pkg)


def _scan_package(package_name: str, base_package: str):
    """Recursively scan a package for skill modules."""
    try:
        package = importlib.import_module(package_name)
    except ImportError:
        return

    package_path = getattr(package, "__path__", [])
    if not package_path:
        return

    for importer, modname, is_pkg in pkgutil.walk_packages(
        package_path, prefix=f"{package_name}."
    ):
        if is_pkg:
            continue

        try:
            module = importlib.import_module(modname)
        except ImportError as e:
            continue

        # Get category from module path relative to skills
        rel_path = modname[len(base_package) + 1:]
        category = "/".join(rel_path.split(".")[:-1])
        skill_name = rel_path.split(".")[-1]

        # Register all public functions (not starting with _)
        for name, func in inspect.getmembers(module, inspect.isfunction):
            if name.startswith("_"):
                continue
            if name == "register_skills":
                # Allow explicit registration
                func()
                continue

            description = _get_description(func, name)
            doc = inspect.getdoc(func) or ""
            skill_tree.register(category, name, func, description, doc)


def _get_description(func: Callable, default_name: str) -> str:
    """Extract a short description from the function."""
    doc = inspect.getdoc(func) or ""
    if doc:
        # Take first line of docstring
        first_line = doc.strip().split("\n")[0]
        if len(first_line) < 100:
            return first_line
    return default_name.replace("_", " ").title()


def register_skill_fn(category: str, name: Optional[str] = None):
    """Decorator to explicitly register a skill function."""
    def decorator(func):
        skill_name = name or func.__name__
        description = _get_description(func, skill_name)
        doc = inspect.getdoc(func) or ""
        skill_tree.register(category, skill_name, func, description, doc)
        return func
    return decorator
