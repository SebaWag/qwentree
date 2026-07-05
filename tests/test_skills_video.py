"""Tests for video/ skills: analyze, extract_frames.

These depend on Qwen-VL API. Tests check error handling.
"""

import pytest


class TestVideoAnalyze:
    """Tests for video/analyze.py"""

    def test_analyze_nonexistent(self):
        from qwentree.skills.video.analyze import analyze
        result = analyze("/nonexistent/video.mp4")
        assert result["success"] is False

    def test_analyze_empty_path(self):
        from qwentree.skills.video.analyze import analyze
        result = analyze("")
        assert result["success"] is False

    def test_video_skills_import(self):
        from qwentree.skills.video import analyze as video_mod
        assert video_mod is not None
        assert hasattr(video_mod, "analyze")


class TestVideoExtractFrames:
    """Tests for video/extract_frames.py"""

    def test_extract_frames_nonexistent(self):
        from qwentree.skills.video.extract_frames import extract_frames
        result = extract_frames("/fake/video.mp4")
        assert result["success"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
