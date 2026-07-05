"""Tests for media/ skills: generate_image, generate_video.

These depend on QwenCloud API (Wan/HappyHorse). Tests check error handling.
"""

import pytest


class TestMediaImage:
    """Tests for media/generate_image.py"""

    def test_generate_image_empty_prompt(self):
        from qwentree.skills.media.generate_image import generate_image
        result = generate_image("")
        assert result["success"] is False
        assert "error" in result

    def test_generate_image_module_import(self):
        from qwentree.skills.media import generate_image as media_mod
        assert media_mod is not None
        assert hasattr(media_mod, "generate_image")


class TestMediaVideo:
    """Tests for media/generate_video (via generate_image module)."""

    def test_media_skills_import(self):
        from qwentree.skills.media.generate_image import generate_image
        from qwentree.skills.media.generate_video import generate_video
        assert generate_image is not None
        assert generate_video is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
