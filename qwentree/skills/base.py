"""Base Skill — Abstract base for all QwenTree skills.

Provides common patterns:
- Metadata & documentation
- Input/output validation
- Error handling
- Integration with Qwen client
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
from qwentree.core.qwen_client import qwen


class BaseSkill(ABC):
    """Abstract base class for skills."""

    name: str = ""
    category: str = ""
    description: str = ""
    requires_qwen: bool = True
    requires_network: bool = False
    requires_filesystem: bool = False

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Execute the skill with given parameters."""
        ...

    def validate_input(self, **kwargs) -> bool:
        """Validate input parameters. Override in subclass."""
        return True

    def format_output(self, result: Any) -> str:
        """Format the skill output for display."""
        if isinstance(result, str):
            return result
        if isinstance(result, dict):
            import json
            return json.dumps(result, indent=2, ensure_ascii=False)
        return str(result)

    @property
    def help_text(self) -> str:
        """Help text for this skill."""
        return (
            f"📄 {self.category}/{self.name}.py\n"
            f"   {self.description}\n"
            f"   Requires: {'Qwen' if self.requires_qwen else 'None'}"
            f"{' | Network' if self.requires_network else ''}"
            f"{' | Filesystem' if self.requires_filesystem else ''}"
        )


def skill(category: str, name: Optional[str] = None,
          description: str = ""):
    """Decorator to register a function as a skill."""
    def decorator(func):
        skill_name = name or func.__name__
        from qwentree.tree import skill_tree
        doc = func.__doc__ or ""
        skill_tree.register(
            category, skill_name, func,
            description or doc.split("\n")[0] if doc else skill_name,
            doc,
        )
        return func
    return decorator
