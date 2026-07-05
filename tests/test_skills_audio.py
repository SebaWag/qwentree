"""Tests for audio/ skills: transcribe, synthesize.

These depend on Qwen-Audio API. Tests check error handling and structure.
"""

import pytest


class TestAudioTranscribe:
    """Tests for audio/transcribe.py"""

    def test_transcribe_nonexistent(self):
        from qwentree.skills.audio.transcribe import transcribe
        result = transcribe("/nonexistent/audio.mp3")
        assert result["success"] is False

    def test_transcribe_empty_path(self):
        from qwentree.skills.audio.transcribe import transcribe
        result = transcribe("")
        assert result["success"] is False

    def test_audio_skills_import(self):
        from qwentree.skills.audio import transcribe as audio_mod
        from qwentree.skills.audio import synthesize
        assert audio_mod is not None
        assert synthesize is not None


class TestAudioSynthesize:
    """Tests for audio/synthesize.py"""

    def test_synthesize_empty_text(self):
        from qwentree.skills.audio.synthesize import synthesize
        result = synthesize("")
        assert result["success"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
