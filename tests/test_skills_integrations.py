"""Tests for integrations/ skills: shiva, n8n, academy."""

import pytest


class TestIntegrations:
    """Tests for integrations module."""

    def test_integrations_import(self):
        from qwentree.skills.integrations import integrations as int_mod
        assert int_mod is not None
        assert hasattr(int_mod, "shiva")
        assert hasattr(int_mod, "n8n")
        assert hasattr(int_mod, "academy")

    def test_shiva_skill_exists(self):
        from qwentree.skills.integrations.integrations import shiva
        assert callable(shiva)

    def test_n8n_skill_exists(self):
        from qwentree.skills.integrations.integrations import n8n
        assert callable(n8n)

    def test_academy_skill_exists(self):
        from qwentree.skills.integrations.integrations import academy
        assert callable(academy)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
