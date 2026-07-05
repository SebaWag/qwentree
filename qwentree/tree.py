"""🌳 QwenTree — Tree File Navigator.

The core concept: skills are organized as a file tree.
The agent navigates this tree like a filesystem:
  ls skills/          → list all skill categories
  ls skills/vision/   → list all vision skills
  cat skills/code/run.md → show skill documentation

Each skill is a "file" that can be:
  - Listado (ls)
  - Leído (cat/read)
  - Ejecutado (run/exec)
  - Documentado (via docstrings/SKILL.md)

This enables the agent to discover its own capabilities dynamically.
"""

import importlib
import inspect
import pkgutil
import os
from pathlib import Path
from typing import Any, Callable, Optional


class SkillNode:
    """A single skill in the tree: a callable capability."""

    def __init__(self, name: str, category: str,
                 func: Callable, description: str = "",
                 doc: str = ""):
        self.name = name
        self.category = category
        self.func = func
        self.description = description or func.__name__
        self.doc = doc or (func.__doc__ or "")
        self.is_async = inspect.iscoroutinefunction(func)

    def __repr__(self) -> str:
        return f"📄 {self.category}/{self.name}.py  →  {self.description}"


class TreeDir:
    """A directory in the skill tree (a category of skills)."""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.skills: dict[str, SkillNode] = {}
        self.subdirs: dict[str, 'TreeDir'] = {}

    def add_skill(self, skill: SkillNode):
        self.skills[skill.name] = skill

    def add_subdir(self, name: str, description: str = "") -> 'TreeDir':
        if name not in self.subdirs:
            self.subdirs[name] = TreeDir(name, description)
        return self.subdirs[name]

    def ls(self, recursive: bool = False, indent: str = "") -> str:
        """List contents of this directory."""
        lines = []
        for sname, skill in sorted(self.skills.items()):
            lines.append(f"{indent}📄 {sname}.py  →  {skill.description}")
        for dname, subdir in sorted(self.subdirs.items()):
            icon = "📁" if subdir.skills or subdir.subdirs else "📂"
            lines.append(f"{indent}{icon} {dname}/")
            if recursive:
                lines.append(subdir.ls(recursive, indent + "  "))
        return "\n".join(lines)

    def total_skills(self) -> int:
        count = len(self.skills)
        for subdir in self.subdirs.values():
            count += subdir.total_skills()
        return count


class SkillTree:
    """🌳 The complete skill tree — agent's capability map."""

    def __init__(self):
        self.root = TreeDir("skills", "Root skill directory")
        self._all_skills: dict[str, SkillNode] = {}

    def register(self, category: str, name: str,
                 func: Callable, description: str = "",
                 doc: str = "") -> SkillNode:
        """Register a skill in the tree."""
        skill = SkillNode(name, category, func, description, doc or func.__doc__)
        self._all_skills[f"{category}/{name}"] = skill

        # Place in tree structure
        parts = category.split("/")
        current = self.root
        for part in parts:
            if part not in current.subdirs:
                current.subdirs[part] = TreeDir(part)
            current = current.subdirs[part]
        current.add_skill(skill)

        return skill

    def get_skill(self, path: str) -> Optional[SkillNode]:
        """Get a skill by path (e.g., 'vision/analyze')."""
        return self._all_skills.get(path)

    def list_skills(self, category: Optional[str] = None,
                    recursive: bool = False) -> list[SkillNode]:
        """List all skills, optionally filtered by category."""
        if not category:
            return list(self._all_skills.values())

        prefix = f"{category}/"
        return [s for path, s in self._all_skills.items()
                if path.startswith(prefix)]

    def find_skill(self, query: str) -> list[SkillNode]:
        """Search skills by name or description."""
        query = query.lower()
        results = []
        for path, skill in self._all_skills.items():
            if query in path.lower() or query in skill.description.lower():
                results.append(skill)
        return results

    def execute(self, path: str, *args, **kwargs) -> Any:
        """Execute a skill by path."""
        skill = self.get_skill(path)
        if not skill:
            raise KeyError(f"Skill not found: {path}")
        return skill.func(*args, **kwargs)

    def tree_display(self) -> str:
        """Full tree display for CLI."""
        return self.root.ls(recursive=True)

    def summary(self) -> dict:
        """Get summary statistics of the skill tree."""
        return {
            "total_skills": len(self._all_skills),
            "categories": len(self.root.subdirs),
            "skills_by_category": {
                name: len(subdir.skills)
                for name, subdir in self.root.subdirs.items()
            },
        }

    def count(self) -> int:
        return len(self._all_skills)


# Singleton
skill_tree = SkillTree()
