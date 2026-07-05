"""Video extract_frames skill using FFmpeg."""
import subprocess
from pathlib import Path

def extract_frames(video_path: str, output_dir: str = "workspace/frames", interval: int = 1) -> dict:
    """Extract frames from video."""
    path = Path(video_path).expanduser().resolve()
    if not path.exists():
        return {"success": False, "error": f"Video not found: {video_path}"}
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        base = path.stem
        output_pattern = str(out_dir / f"{base}_frame_%04d.jpg")
        result = subprocess.run(["ffmpeg", "-i", str(path), "-vf", f"fps=1/{interval}", "-q:v", "2", output_pattern], capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            return {"success": False, "error": f"FFmpeg error: {result.stderr[:500]}"}
        frames = sorted(out_dir.glob(f"{base}_frame_*.jpg"))
        return {"success": True, "frames": [str(f) for f in frames], "count": len(frames), "output_dir": str(out_dir)}
    except Exception as e:
        return {"success": False, "error": str(e)}
