"""Tests for system/ skills: exec_command, info."""

import pytest


class TestSystemExec:
    """Tests for system/exec.py"""

    def test_exec_simple(self):
        from qwentree.skills.system.exec import exec_command
        result = exec_command("echo hello from qwentree")
        assert result["success"] is True
        assert "hello from qwentree" in result["stdout"]

    def test_exec_failure(self):
        from qwentree.skills.system.exec import exec_command
        result = exec_command("exit 1")
        assert result["success"] is False
        assert result["returncode"] == 1

    def test_exec_ls(self):
        from qwentree.skills.system.exec import exec_command
        result = exec_command("ls -la")
        assert result["success"] is True
        assert result["returncode"] == 0


class TestSystemInfo:
    """Tests for system/info.py"""

    def test_info_returns_dict(self):
        from qwentree.skills.system.info import info
        result = info()
        assert result["success"] is True
        assert isinstance(result, dict)

    def test_info_has_keys(self):
        from qwentree.skills.system.info import info
        result = info()
        keys_found = set(result.keys())
        # Should have meaningful system info keys
        assert len(result) > 2, f"Too few keys: {keys_found}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
