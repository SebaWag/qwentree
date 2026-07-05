"""🎬 video/analyze — Analyze video content using Qwen-VL + FFmpeg."""

from qwentree.core.qwen_client import qwen
import os


def analyze(video_path: str, prompt: str = "Describe what happens in this video.",
            num_frames: int = 8) -> dict:
    """Analyze a video by extracting key frames and using Qwen-VL.

    Requires FFmpeg for frame extraction.

    Args:
        video_path: Path to the video file
        prompt: What to ask about the video
        num_frames: Number of frames to extract for analysis
    Returns:
        dict with video analysis
    """
    if not os.path.exists(video_path):
        return {"success": False, "error": f"Video not found: {video_path}"}

    try:
        description = qwen.analyze_video(video_path, prompt, num_frames)
        return {
            "success": True,
            "analysis": description,
            "video": video_path,
            "frames_analyzed": num_frames,
            "model": "qwen-vl-max",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def extract_frames(video_path: str, output_dir: str = "workspace/frames",
                   num_frames: int = 10) -> dict:
    """Extract key frames from a video.

    Args:
        video_path: Path to video file
        output_dir: Directory to save frames
        num_frames: Number of frames to extract
    Returns:
        dict with frame paths
    """
    import subprocess
    from pathlib import Path

    if not os.path.exists(video_path):
        return {"success": False, "error": f"Video not found: {video_path}"}

    os.makedirs(output_dir, exist_ok=True)

    # Get video duration
    duration_cmd = [
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
        video_path,
    ]
    result = subprocess.run(duration_cmd, capture_output=True, text=True)
    duration = float(result.stdout.strip()) if result.stdout.strip() else 0

    if duration <= 0:
        return {"success": False, "error": "Could not determine video duration"}

    frame_paths = []
    for i in range(num_frames):
        timestamp = (duration / (num_frames + 1)) * (i + 1)
        frame_path = f"{output_dir}/frame_{i:03d}.jpg"
        subprocess.run([
            "ffmpeg", "-ss", str(timestamp), "-i", video_path,
            "-vframes", "1", "-q:v", "2", frame_path,
        ], capture_output=True)
        frame_paths.append(frame_path)

    return {
        "success": True,
        "frames": frame_paths,
        "num_frames": len(frame_paths),
        "video_duration": duration,
        "output_dir": output_dir,
    }
