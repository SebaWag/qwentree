"""Pytest fixtures for QwenTree tests."""

import os
import sys
import pytest
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """Ensure Qwen API key is properly configured for all tests."""
    # Import settings inside fixture to get real config
    from qwentree.core.config import settings

    # Export the real API key to environment variables
    if settings.qwen_api_key:
        monkeypatch.setenv("QWEN_API_KEY", settings.qwen_api_key)
        monkeypatch.setenv("OPENAI_API_KEY", settings.qwen_api_key)
        monkeypatch.setenv("API_MODE", "qwen")
        # Also force the settings object to use correct mode
        settings.api_mode = "qwen"


@pytest.fixture
def temp_dir():
    """Create a temporary directory for file operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        old_cwd = os.getcwd()
        os.chdir(tmpdir)
        yield Path(tmpdir)
        os.chdir(old_cwd)


@pytest.fixture
def sample_file(temp_dir):
    """Create a sample text file for testing."""
    f = temp_dir / "test.txt"
    f.write_text("Hello, QwenTree!\nThis is a test file.\nLine 3\nLine 4\nLine 5")
    return f


@pytest.fixture
def skill_tree():
    """Get the skill tree singleton."""
    from qwentree.tree import skill_tree
    return skill_tree


@pytest.fixture
def registry():
    """Auto-register all skills and return the module."""
    from qwentree.core import registry
    registry.auto_register_skills()
    return registry


@pytest.fixture
def terminal():
    """Get the terminal sandbox singleton."""
    from qwentree.core.terminal import terminal
    return terminal
