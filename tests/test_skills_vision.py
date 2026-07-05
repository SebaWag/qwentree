"""Tests for vision/ skills: analyze, analyze_url, ocr.

These skills depend on Qwen-VL API. Tests use fallback mode by default.
"""

import pytest


class TestVisionAnalyze:
    """Tests for vision/analyze.py"""

    def test_analyze_nonexistent_image(self):
        """Without a real image, should return error gracefully."""
        from qwentree.skills.vision.analyze import analyze
        result = analyze("/nonexistent/image.png", "Describe this")
        assert result["success"] is False
        assert "error" in result

    def test_analyze_url_empty(self):
        """Analyze with empty URL returns error."""
        from qwentree.skills.vision.analyze import analyze_url
        result = analyze_url("", "Describe")
        assert result["success"] is False

    def test_analyze_invalid_url(self):
        """Invalid URL returns error (no crash)."""
        from qwentree.skills.vision.analyze import analyze_url
        result = analyze_url("not-a-url", "Describe")
        assert result["success"] is False

    def test_ocr_nonexistent(self):
        """OCR on nonexistent file returns error."""
        from qwentree.skills.vision.analyze import ocr
        result = ocr("/fake/image.png")
        assert result["success"] is False

    def test_vision_skills_import(self):
        """Module imports without error."""
        from qwentree.skills.vision import analyze
        assert analyze is not None
        assert hasattr(analyze, "analyze")
        assert hasattr(analyze, "analyze_url")
        assert hasattr(analyze, "ocr")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
