"""Tests for files/ skills."""

import pytest
import json
from pathlib import Path


class TestFilesRead:
    def test_read_file(self, temp_dir):
        from qwentree.skills.files.read import read
        f = temp_dir / "hello.txt"
        f.write_text("Hello QwenTree!")
        result = read(str(f))
        assert result["success"] is True
        assert result["content"] == "Hello QwenTree!"

    def test_read_file_not_found(self):
        from qwentree.skills.files.read import read
        result = read("/nonexistent/file.txt")
        assert result["success"] is False
        assert "not found" in result["error"].lower()

    def test_read_file_metadata(self, temp_dir):
        from qwentree.skills.files.read import read
        f = temp_dir / "meta.txt"
        f.write_text("test")
        result = read(str(f))
        assert "path" in result
        assert "size" in result
        assert "extension" in result

    def test_read_lines(self, temp_dir):
        from qwentree.skills.files.read import read_lines
        f = temp_dir / "lines.txt"
        f.write_text("Line0\nLine1\nLine2\nLine3\nLine4\n")
        result = read_lines(str(f), start=1, end=3)
        assert result["success"] is True
        assert result["lines"] == ["Line1", "Line2"]

    def test_read_lines_not_found(self):
        from qwentree.skills.files.read import read_lines
        result = read_lines("/fake/file.py")
        assert result["success"] is False


class TestFilesWrite:
    def test_write_file(self, temp_dir):
        from qwentree.skills.files.write import write
        path = str(temp_dir / "new_file.txt")
        result = write(path, "Hello from QwenTree!")
        assert result["success"] is True
        assert Path(path).read_text() == "Hello from QwenTree!"

    def test_write_file_overwrite(self, temp_dir):
        from qwentree.skills.files.write import write
        path = str(temp_dir / "overwrite.txt")
        write(path, "Original")
        result = write(path, "Overwritten")
        assert result["success"] is True
        assert Path(path).read_text() == "Overwritten"

    def test_write_nested_dirs(self, temp_dir):
        from qwentree.skills.files.write import write
        path = str(temp_dir / "nested" / "deep" / "file.txt")
        result = write(path, "Nested file created")
        assert result["success"] is True
        assert Path(path).exists()

    def test_write_json(self, temp_dir):
        from qwentree.skills.files.write import write
        path = str(temp_dir / "data.json")
        data = {"name": "QwenTree", "version": "1.0"}
        result = write(path, json.dumps(data))
        assert result["success"] is True
        loaded = json.loads(Path(path).read_text())
        assert loaded["name"] == "QwenTree"


class TestFilesSearch:
    def test_search_by_pattern(self, temp_dir):
        from qwentree.skills.files.search import search
        (temp_dir / "script.py").write_text("print(hello)")
        (temp_dir / "notes.txt").write_text("some notes")
        # search(pattern, search_path) - busca archivos por nombre
        result = search("*.py", str(temp_dir))
        assert result["success"] is True
        assert len(result["results"]) >= 1
        assert any("script.py" in r["path"] for r in result["results"])

    def test_search_no_results(self, temp_dir):
        from qwentree.skills.files.search import search
        (temp_dir / "plain.txt").write_text("Nothing special")
        result = search("*.nonexistent", str(temp_dir))
        assert result["success"] is True
        assert len(result["results"]) == 0

    def test_search_nonexistent_dir(self):
        from qwentree.skills.files.search import search
        result = search("*", "/nonexistent_dir_12345")
        assert result["success"] is False


class TestFilesTree:
    def test_tree_basic(self, temp_dir):
        from qwentree.skills.files.tree import tree
        (temp_dir / "subdir").mkdir()
        (temp_dir / "subdir" / "nested.txt").write_text("nested")
        (temp_dir / "root.txt").write_text("root")
        result = tree(str(temp_dir))
        assert result["success"] is True
        assert "tree_text" in result
        assert "structure" in result
        assert "subdir" in result["tree_text"] or "root.txt" in result["tree_text"]

    def test_tree_nonexistent(self):
        from qwentree.skills.files.tree import tree
        result = tree("/fake_path_12345")
        assert result["success"] is False


class TestFilesAppend:
    def test_append_to_file(self, temp_dir):
        from qwentree.skills.files.write import write
        path = str(temp_dir / "log.txt")
        write(path, "Line 1\n")
        result = write(path, "Line 2\n", mode="a")
        assert result["success"] is True
        content = Path(path).read_text()
        assert "Line 1" in content
        assert "Line 2" in content


class TestFilesFindByContent:
    def test_find_by_content(self, temp_dir):
        from qwentree.skills.files.search import find_by_content
        (temp_dir / "doc1.md").write_text("Some SECRET content here")
        (temp_dir / "doc2.md").write_text("Different content")
        # find_by_content(query, search_path, file_pattern)
        result = find_by_content("SECRET", str(temp_dir), "*")
        assert result["success"] is True
        assert len(result["results"]) >= 1

    def test_find_by_content_single(self, temp_dir):
        from qwentree.skills.files.search import find_by_content
        (temp_dir / "unique.txt").write_text("UNIQUE_MATCH_12345")
        result = find_by_content("UNIQUE_MATCH_12345", str(temp_dir), "*")
        assert result["success"] is True
        assert len(result["results"]) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
