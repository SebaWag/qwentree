"""Media generate_video skill using HappyHorse."""
from qwentree.core.qwen_client import qwen

def generate_video(prompt: str, output_path: str = "workspace/demo.mp4") -> dict:
    """Generate video from text."""
    try:
        if not prompt or not prompt.strip():
            return {"success": False, "error": "Empty prompt"}
        result = qwen.generate_video(prompt, output_path)
        return {"success": True, "path": result, "prompt": prompt[:100], "model": "happyhorse-1.1-t2v"}
    except Exception as e:
        return {"success": False, "error": str(e)}
