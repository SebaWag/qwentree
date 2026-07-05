"""🎤 audio/transcribe — Transcribe audio to text using Qwen-Audio."""

from qwentree.core.qwen_client import qwen
import os


def transcribe(audio_path: str) -> dict:
    """Transcribe an audio file to text using Qwen-Audio.

    Supports: mp3, wav, m4a, ogg, flac

    Args:
        audio_path: Path to the audio file
    Returns:
        dict with transcription
    """
    if not os.path.exists(audio_path):
        return {"success": False, "error": f"Audio file not found: {audio_path}"}

    try:
        text = qwen.transcribe_audio(audio_path)
        return {
            "success": True,
            "transcription": text,
            "audio_file": audio_path,
            "model": "qwen-audio",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def synthesize(text: str, output_path: str = "workspace/speech.mp3",
               voice: str = "longxiaochun") -> dict:
    """Convert text to speech using CosyVoice (Alibaba Cloud TTS).

    Args:
        text: Text to synthesize
        output_path: Where to save the audio file
        voice: Voice to use (longxiaochun, longxiaoxia, etc.)
    Returns:
        dict with path to generated audio
    """
    try:
        result = qwen.synthesize_speech(text, output_path, voice=voice)
        return {
            "success": True,
            "audio_path": result,
            "text_length": len(text),
            "model": "cosyvoice-01",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
