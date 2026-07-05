"""👁️ vision/analyze — Analyze images using Qwen-VL."""

from qwentree.core.qwen_client import qwen


def analyze(image_path: str, prompt: str = "Describe this image in detail.") -> dict:
    """Analyze an image file using Qwen-VL multimodal model.

    Args:
        image_path: Path to the image file (jpg, png, gif, webp)
        prompt: What to ask about the image
    Returns:
        dict with analysis text
    """
    try:
        result = qwen.analyze_image(image_path, prompt)
        return {
            "success": True,
            "analysis": result,
            "image": image_path,
            "model": "qwen-vl-max",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def analyze_url(image_url: str, prompt: str = "Describe this image in detail.") -> dict:
    """Analyze an image from URL using Qwen-VL."""
    try:
        result = qwen.analyze_image_url(image_url, prompt)
        return {
            "success": True,
            "analysis": result,
            "image_url": image_url,
            "model": "qwen-vl-max",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def ocr(image_path: str) -> dict:
    """Extract text from an image using Qwen-VL (OCR).

    Args:
        image_path: Path to the image file
    Returns:
        dict with extracted text
    """
    try:
        text = qwen.extract_text_from_image(image_path)
        return {
            "success": True,
            "extracted_text": text,
            "image": image_path,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
