"""Tests for QwenTree Core: Config, Tree, Registry, Terminal."""

import os
import pytest
from pathlib import Path


class TestConfig:
    """Tests for configuration."""

    def test_settings_import(self):
        from qwentree.core.config import Settings, settings
        assert settings is not None
        assert isinstance(settings, Settings)

    def test_settings_has_required_fields(self):
        from qwentree.core.config import settings
        assert hasattr(settings, "api_mode")
        assert hasattr(settings, "chroma_host")
        assert hasattr(settings, "chroma_port")
        assert settings.api_mode in ("qwen", "fallback")
        print(f"  API Mode: {settings.api_mode}")
        print(f"  Chroma: {settings.chroma_host}:{settings.chroma_port}")

    def test_settings_qwen_mode(self):
        from qwentree.core.config import Settings
        s = Settings(api_mode="qwen", qwen_api_key="sk-test-123")
        assert s.is_qwen_mode is True
        assert "dashscope-intl" in s.active_base_url

    def test_settings_fallback_mode(self):
        from qwentree.core.config import Settings
        s = Settings(api_mode="fallback", fallback_model="gpt-4o")
        assert s.is_qwen_mode is False
        assert s.active_model == "gpt-4o"

    def test_settings_properties(self):
        from qwentree.core.config import Settings
        s = Settings(api_mode="qwen", qwen_api_key="sk-test", qwen_model="qwen3.7-plus")
        assert s.active_api_key == "sk-test"
        assert "dashscope-intl" in s.active_base_url
        assert s.active_model == "qwen3.7-plus"

    def test_settings_env_override(self):
        """Settings can be created with env vars without corrupting global singleton."""
        from qwentree.core.config import Settings
        # Create a temporary settings instance with overrides
        s = Settings(api_mode="fallback", chroma_host="test-host")
        assert s.api_mode == "fallback"
        assert s.chroma_host == "test-host"
        # Global settings should be unaffected
        from qwentree.core.config import settings as global_settings
        assert global_settings.api_mode == "qwen" or global_settings.api_mode == "fallback"


class TestTree:
    """Tests for SkillTree (tree.py)."""

    def test_skill_tree_singleton(self, skill_tree):
        from qwentree.tree import SkillTree
        assert isinstance(skill_tree, SkillTree)

    def test_register_skill(self, skill_tree):
        def dummy_func():
            return "hello"
        skill = skill_tree.register("test", "dummy", dummy_func, "A test skill")
        assert skill.name == "dummy"
        assert skill.category == "test"
        retrieved = skill_tree.get_skill("test/dummy")
        assert retrieved is not None

    def test_execute_skill(self, skill_tree):
        def add(a, b):
            return a + b
        skill_tree.register("math", "add", add, "Add two numbers")
        result = skill_tree.execute("math/add", 3, 4)
        assert result == 7

    def test_execute_nonexistent_skill(self, skill_tree):
        with pytest.raises(KeyError):
            skill_tree.execute("nonexistent/foo")

    def test_list_skills(self, skill_tree):
        skill_tree.register("cat_a", "func1", lambda: 1)
        skill_tree.register("cat_a", "func2", lambda: 2)
        skill_tree.register("cat_b", "func3", lambda: 3)
        assert len(skill_tree.list_skills("cat_a")) == 2
        assert len(skill_tree.list_skills()) >= 3

    def test_find_skill(self, skill_tree):
        skill_tree.register("search_test", "find_me", lambda: 0, "unique xyz")
        results = skill_tree.find_skill("unique xyz")
        assert len(results) >= 1

    def test_tree_display(self, skill_tree):
        assert isinstance(skill_tree.tree_display(), str)

    def test_summary(self, skill_tree):
        s = skill_tree.summary()
        assert "total_skills" in s
        assert "categories" in s

    def test_count(self, skill_tree):
        assert isinstance(skill_tree.count(), int)

    def test_skill_node_repr(self, skill_tree):
        skill_tree.register("repr_test", "my_skill", lambda: 0, "does something")
        skill = skill_tree.get_skill("repr_test/my_skill")
        assert "my_skill" in repr(skill)


class TestRegistry:
    """Tests for auto-registration of skills."""

    def test_auto_register_discovers_skills(self, registry, skill_tree):
        count = skill_tree.count()
        print(f"Skills registered: {count}")
        assert count > 0
        for skill_path in ["files/read", "vision/analyze", "system/info"]:
            skill = skill_tree.get_skill(skill_path)
            assert skill is not None, f"Skill {skill_path} not registered"

    def test_skills_list_categories(self, registry, skill_tree):
        summary = skill_tree.summary()
        print(f"Categories: {summary['categories']}, Skills: {summary['total_skills']}")
        print(f"By category: {summary['skills_by_category']}")
        assert summary["categories"] > 0
        assert summary["total_skills"] > 10


class TestTerminal:
    """Tests for TerminalSandbox."""

    def test_terminal_singleton(self, terminal):
        from qwentree.core.terminal import TerminalSandbox
        assert isinstance(terminal, TerminalSandbox)

    def test_run_simple_command(self, terminal):
        r = terminal.run("echo 'Hello QwenTree'", timeout=5)
        assert r["success"] is True
        assert "Hello QwenTree" in r["stdout"]

    def test_run_command_failure(self, terminal):
        r = terminal.run("exit 42", timeout=5)
        assert r["success"] is False
        assert r["returncode"] == 42

    def test_run_python(self, terminal):
        r = terminal.run_python("print(2 + 2)", timeout=5)
        assert r["success"] is True
        assert "4" in r["stdout"]

    def test_run_python_syntax_error(self, terminal):
        r = terminal.run_python("if True print('no colon')", timeout=5)
        assert r["success"] is False

    def test_run_script_nonexistent(self, terminal):
        r = terminal.run_script("/nonexistent/script.py", timeout=5)
        assert r["success"] is False
        assert "not found" in r["stderr"].lower()

    def test_history(self, terminal):
        terminal.clear_history()
        terminal.run("echo 'first'", timeout=5)
        terminal.run("echo 'second'", timeout=5)
        assert len(terminal.get_history(10)) == 2

    def test_summary_stats(self, terminal):
        s = terminal.summary
        assert "total_commands" in s
        assert "successful" in s
        assert "workspace" in s


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
