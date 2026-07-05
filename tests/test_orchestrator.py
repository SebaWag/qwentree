"""Tests for orchestrator.py — the main router."""

import pytest


class TestOrchestrator:
    """Tests for the QwenTree orchestrator."""

    def test_orchestrator_import(self):
        from qwentree.orchestrator import orchestrator
        assert orchestrator is not None

    def test_orchestrator_has_process(self):
        from qwentree.orchestrator import orchestrator
        assert hasattr(orchestrator, "process")

    def test_orchestrator_has_system_prompt(self):
        from qwentree.orchestrator import ORCHESTRATOR_SYSTEM_PROMPT
        assert ORCHESTRATOR_SYSTEM_PROMPT is not None
        assert len(ORCHESTRATOR_SYSTEM_PROMPT) > 100

    def test_orchestrator_system_prompt_mentions_skills(self):
        from qwentree.orchestrator import ORCHESTRATOR_SYSTEM_PROMPT
        categories = ["vision", "audio", "code", "files", "web", "system", "memory", "media"]
        for cat in categories:
            assert cat in ORCHESTRATOR_SYSTEM_PROMPT.lower(), f"Category {cat} not in prompt"

    def test_orchestrator_processes_basic_query(self):
        """Process a simple query using the configured API (QwenCloud)."""
        from qwentree.core.registry import auto_register_skills
        from qwentree.orchestrator import orchestrator

        auto_register_skills()
        result = orchestrator.process("Say hello in one word")
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
        # The response should contain a greeting
        assert "hello" in result.lower() or "hi" in result.lower() or "hola" in result.lower() or "hey" in result.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
