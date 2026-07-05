"""Audio synthesize skill using CosyVoice."""
from qwentree.core.qwen_client import qwen

def synthesize(text: str, output_path: str = "workspace/speech.mp3") -> dict:
    """Convert text to speech."""
    try:
        if not text or not text.strip():
            return {"success": False, "error": "Empty text"}
        result = qwen.synthesize_speech(text, output_path)
        return {"success": True, "path": result, "text": text[:100], "model": "cosyvoice-01"}
    except Exception as e:
        return {"success": False, "error": str(e)}
