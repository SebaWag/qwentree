"""Tests for web/ skills: search, fetch."""

import pytest


class TestWebSearch:
    """Tests for web/search.py"""

    def test_search_empty_query(self):
        from qwentree.skills.web.search import search
        result = search("")
        assert result["success"] is False

    def test_fetch_empty_url(self):
        from qwentree.skills.web.search import fetch
        result = fetch("")
        assert result["success"] is False

    def test_fetch_invalid_url(self):
        from qwentree.skills.web.search import fetch
        result = fetch("not-a-valid-url")
        assert result["success"] is False

    def test_web_skills_import(self):
        from qwentree.skills.web import search as web_mod
        assert web_mod is not None
        assert hasattr(web_mod, "search")
        assert hasattr(web_mod, "fetch")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
