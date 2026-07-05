"""Tests for code/ skills: analyze, run, run_file, run_shell."""

import pytest
from pathlib import Path


class TestCodeRun:
    """Tests for code/run.py"""

    def test_run_python_code(self, temp_dir):
        from qwentree.skills.code.run import run
        code = "print(sum(range(10)))"
        result = run(code)
        assert result["success"] is True
        assert "45" in result["stdout"]

    def test_run_python_syntax_error(self, temp_dir):
        from qwentree.skills.code.run import run
        code = "if True print(no colon)"
        result = run(code)
        assert result["success"] is False

    def test_run_file(self, temp_dir):
        from qwentree.skills.code.run import run_file
        f = temp_dir / "script.py"
        f.write_text("print(2**10)")
        result = run_file(str(f))
        assert result["success"] is True
        assert "1024" in result["stdout"]

    def test_run_file_not_found(self):
        from qwentree.skills.code.run import run_file
        result = run_file("/nonexistent.py")
        assert result["success"] is False

    def test_run_shell(self, temp_dir):
        from qwentree.skills.code.run import run_shell
        result = run_shell("echo shell test")
        assert result["success"] is True
        assert "shell test" in result["stdout"]


class TestCodeAnalyze:
    """Tests for code/analyze.py"""

    def test_analyze_python(self, temp_dir):
        from qwentree.skills.code.analyze import analyze
        f = temp_dir / "test_script.py"
        f.write_text("""def hello(name):
    \"\"\"Say hello.\"\"\"
    return f"Hello {name}"

x = 42
print(hello("world"))
""")
        result = analyze(str(f))
        assert result["success"] is True
        assert result["summary"]["functions"] >= 1
        assert result["summary"]["lines_of_code"] >= 5

    def test_analyze_file_not_found(self):
        from qwentree.skills.code.analyze import analyze
        result = analyze("/nonexistent/file.py")
        assert result["success"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
