"""Tests for memory/ skills: recall, search.

These interact with the 3-tier memory system (ChromaDB, PostgreSQL, Redis).
Uses the real Qwen API key for embeddings.
"""

import pytest


class TestMemoryRecall:
    """Tests for memory/recall.py"""

    def test_memory_skills_import(self):
        from qwentree.skills.memory import recall as mem_mod
        assert mem_mod is not None
        assert hasattr(mem_mod, "recall")
        assert hasattr(mem_mod, "search")

    def test_recall_empty_query(self):
        from qwentree.skills.memory.recall import recall
        result = recall("", limit=1)
        assert result["success"] is True
        assert "total_results" in result
        assert "formatted_context" in result

    def test_recall_returns_structure(self):
        from qwentree.skills.memory.recall import recall
        result = recall("QwenTree test query", limit=3)
        assert result["success"] is True
        assert "mental_models" in result
        assert "observations" in result
        assert "raw_facts" in result
        assert "total_results" in result

    def test_search_specific_tier(self):
        from qwentree.skills.memory.recall import search
        result = search("test", tier="mental_models")
        assert result["success"] is True
        assert result["tier"] == "mental_models"

    def test_search_invalid_tier_defaults(self):
        from qwentree.skills.memory.recall import search
        result = search("test", tier="invalid_tier")
        assert result["success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
