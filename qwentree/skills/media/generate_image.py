"""🎨 media/generate_image — Generate images using Wan (QwenCloud)."""

from qwentree.core.qwen_client import qwen
from qwentree.core.config import settings


def generate_image(prompt: str, output_path: str = "workspace/generated.png",
                   size: str = "1024x1024") -> dict:
    """Generate an image from a text description using Wan model.

    Uses QwenCloud's Wan text-to-image model.

    Args:
        prompt: Detailed description of the image to generate
        output_path: Where to save the generated image
        size: Image size (e.g., "1024x1024", "1920x1080", "768x768")
    Returns:
        dict with path to generated image and metadata
    """
    try:
        result_path = qwen.generate_image(prompt, output_path, size=size)

        import os
        file_size = os.path.getsize(result_path) if os.path.exists(result_path) else 0

        return {
            "success": True,
            "image_path": result_path,
            "prompt": prompt,
            "size": size,
            "file_size_bytes": file_size,
            "model": settings.qwen_image_model,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def generate_video(prompt: str, output_path: str = "workspace/generated.mp4",
                   duration: int = 5) -> dict:
    """Generate a video from a text description using Wan-Video.

    Uses QwenCloud's Wan text-to-video model.

    Args:
        prompt: Detailed description of the video to generate
        output_path: Where to save the generated video
        duration: Video duration in seconds (max: 10)
    Returns:
        dict with path to generated video
    """
    try:
        import httpx
        import json

        # Wan-Video uses a different async generation workflow
        # First, submit the generation task
        url = f"{settings.qwen_base_url}/video/generations"
        headers = {
            "Authorization": f"Bearer {settings.active_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.qwen_video_model or "wan-video",
            "input": {
                "prompt": prompt,
            },
            "parameters": {
                "duration": duration,
                "size": "1280x720",
            },
        }

        resp = httpx.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        task_data = resp.json()

        # Poll for completion (Wan-Video is async)
        task_id = task_data.get("task_id", "")
        if not task_id:
            return {"success": False, "error": "No task_id returned from Wan-Video"}

        status_url = f"{settings.qwen_base_url}/video/generations/{task_id}"
        import time

        for _ in range(60):  # Wait up to 5 minutes
            status_resp = httpx.get(status_url, headers=headers, timeout=30)
            status_data = status_resp.json()
            status = status_data.get("status", "")

            if status == "succeeded":
                video_url = status_data.get("output", {}).get("video_url", "")
                if video_url:
                    video_resp = httpx.get(video_url, timeout=60)
                    with open(output_path, "wb") as f:
                        f.write(video_resp.content)

                    import os
                    return {
                        "success": True,
                        "video_path": output_path,
                        "prompt": prompt,
                        "duration": duration,
                        "file_size_bytes": os.path.getsize(output_path),
                        "model": settings.qwen_video_model,
                    }
                break
            elif status == "failed":
                error_msg = status_data.get("message", "Unknown error")
                return {"success": False, "error": f"Generation failed: {error_msg}"}

            time.sleep(5)

        return {"success": False, "error": "Generation timed out"}

    except Exception as e:
        return {"success": False, "error": str(e)}
