"""QwenTree QwenCloud Client — Multimodal Unified Client.

Single client for ALL Qwen models:
  - Text: qwen3.7-plus, qwen3.7-max, qwen-coder-plus
  - Vision: qwen-vl-max, qwen-vl-plus (image + video)
  - Audio: qwen-audio (STT), cosyvoice-01 (TTS)
  - Embeddings: text-embedding-v3
  - Media: wan (image gen), wan-video (video gen)

All through OpenAI-compatible API. Drop-in for any endpoint.
"""

import json
import base64
from typing import Optional, Union
from openai import OpenAI
from qwentree.core.config import settings


class QwenClient:
    """Unified multimodal client for all Qwen Cloud models."""

    def __init__(self):
        self._client: Optional[OpenAI] = None
        self._current_mode: Optional[str] = None

    @property
    def client(self) -> OpenAI:
        """Get or recreate the OpenAI-compatible client."""
        mode = settings.api_mode
        api_key = settings.active_api_key
        base_url = settings.active_base_url

        if self._client is None or self._current_mode != mode:
            self._client = OpenAI(api_key=api_key, base_url=base_url)
            self._current_mode = mode
        return self._client

    # ============================================================
    # TEXT & REASONING
    # ============================================================

    def chat(self, messages: list[dict], temperature: float = 0.3,
             max_tokens: Optional[int] = None,
             tools: Optional[list] = None,
             model: Optional[str] = None) -> OpenAI:
        """Chat completion with any text model."""
        kwargs = {
            "model": model or settings.active_model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens:
            kwargs["max_tokens"] = max_tokens
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        return self.client.chat.completions.create(**kwargs)

    def chat_deep(self, messages: list[dict], **kwargs) -> OpenAI:
        """Deep reasoning with Qwen-Max (orchestrator)."""
        return self.chat(messages, model=settings.qwen_model_max, **kwargs)

    def chat_code(self, messages: list[dict], **kwargs) -> OpenAI:
        """Code-specific with Qwen-Coder."""
        return self.chat(messages, model=settings.qwen_coder_model,
                        temperature=0.2, **kwargs)

    # ============================================================
    # VISION — Image & Video Analysis
    # ============================================================

    def analyze_image(self, image_path: str, prompt: str = "Describe this image in detail.",
                      model: Optional[str] = None) -> str:
        """Analyze an image file with Qwen-VL."""
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")

        ext = image_path.split(".")[-1].lower()
        mime = f"image/{'jpeg' if ext in ('jpg', 'jpeg') else ext}"

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {
                        "url": f"data:{mime};base64,{b64}"
                    }},
                ],
            }
        ]
        resp = self.chat(messages, model=model or settings.qwen_vl_model)
        return resp.choices[0].message.content

    def analyze_image_url(self, image_url: str, prompt: str = "Describe this image in detail.",
                          model: Optional[str] = None) -> str:
        """Analyze an image from URL with Qwen-VL."""
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ]
        resp = self.chat(messages, model=model or settings.qwen_vl_model)
        return resp.choices[0].message.content

    def extract_text_from_image(self, image_path: str) -> str:
        """OCR: Extract text from image using Qwen-VL."""
        return self.analyze_image(
            image_path,
            prompt="Extract all text from this image. Return ONLY the text, no descriptions.",
        )

    # ============================================================
    # AUDIO — Speech-to-Text & Text-to-Speech
    # ============================================================

    def transcribe_audio(self, audio_path: str,
                         model: Optional[str] = None) -> str:
        """Transcribe audio file to text using Qwen-Audio."""
        with open(audio_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")

        ext = audio_path.split(".")[-1].lower()
        mime = f"audio/{ext}"

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Transcribe this audio exactly as spoken."},
                    {"type": "audio_url", "audio_url": {
                        "url": f"data:{mime};base64,{b64}"
                    }},
                ],
            }
        ]
        resp = self.chat(messages, model=model or settings.qwen_audio_model)
        return resp.choices[0].message.content

    def synthesize_speech(self, text: str, output_path: str,
                          voice: str = "longxiaochun",
                          model: Optional[str] = None) -> str:
        """Text-to-Speech using CosyVoice (Alibaba Cloud).

        Args:
            text: Text to synthesize
            output_path: Path to save audio file
            voice: Voice ID (default: longxiaochun)
                   Options: longxiaochun, longxiaoxia, longxiaomeng, etc.
        Returns:
            Path to generated audio file
        """
        import httpx

        # CosyVoice uses a different API endpoint
        url = f"{settings.qwen_base_url}/audio/speech"
        headers = {
            "Authorization": f"Bearer {settings.active_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model or settings.qwen_tts_model,
            "input": {"text": text},
            "voice": voice,
            "response_format": "mp3",
            "sample_rate": 24000,
        }

        resp = httpx.post(url, headers=headers, json=payload)
        resp.raise_for_status()

        with open(output_path, "wb") as f:
            f.write(resp.content)

        return output_path

    # ============================================================
    # VIDEO — Frame Extraction & Analysis
    # ============================================================

    def analyze_video(self, video_path: str,
                      prompt: str = "Describe what happens in this video.",
                      num_frames: int = 8,
                      model: Optional[str] = None) -> str:
        """Analyze a video by extracting key frames and sending to Qwen-VL.

        Uses FFmpeg to extract frames, then sends them as image inputs.
        """
        import subprocess
        import os

        # Get video duration
        duration_cmd = [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
            video_path,
        ]
        result = subprocess.run(duration_cmd, capture_output=True, text=True)
        duration = float(result.stdout.strip())

        # Extract frames at regular intervals
        frames_dir = f"/tmp/qwentree_frames_{os.getpid()}"
        os.makedirs(frames_dir, exist_ok=True)

        frame_paths = []
        for i in range(num_frames):
            timestamp = (duration / (num_frames + 1)) * (i + 1)
            frame_path = f"{frames_dir}/frame_{i:03d}.jpg"
            subprocess.run([
                "ffmpeg", "-ss", str(timestamp), "-i", video_path,
                "-vframes", "1", "-q:v", "2", frame_path,
            ], capture_output=True)
            frame_paths.append(frame_path)

        # Build multimodal message with frames
        content = [{"type": "text", "text": prompt}]
        for fp in frame_paths:
            with open(fp, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
            })

        messages = [{"role": "user", "content": content}]
        resp = self.chat(messages, model=model or settings.qwen_vl_model)

        # Cleanup
        import shutil
        shutil.rmtree(frames_dir, ignore_errors=True)

        return resp.choices[0].message.content

    # ============================================================
    # MEDIA GENERATION — Images & Video (Wan models)
    # ============================================================

    def generate_image(self, prompt, output_path, size="1024x1024", model=None, timeout_seconds=120):
        import httpx, time
        api_key = settings.active_api_key
        model_name = model or "wanx-v1"
        headers = {
            "Authorization": "Bearer " + api_key,
            "X-DashScope-Async": "enable",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model_name,
            "input": {"prompt": prompt},
            "parameters": {"size": size.replace("x", "*"), "n": 1},
        }
        url = "https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
        resp = httpx.post(url, headers=headers, json=payload, timeout=30)
        data = resp.json()
        if "output" not in data or "task_id" not in data["output"]:
            raise RuntimeError("Wan failed: " + data.get("message", "unknown"))
        task_id = data["output"]["task_id"]
        poll_h = {"Authorization": "Bearer " + api_key}
        start = time.time()
        while time.time() - start < timeout_seconds:
            time.sleep(3)
            surl = "https://dashscope-intl.aliyuncs.com/api/v1/tasks/" + task_id
            s = httpx.get(surl, headers=poll_h, timeout=15)
            sd = s.json()
            st = sd.get("output", {}).get("task_status", "UNKNOWN")
            if st == "SUCCEEDED":
                results = sd.get("output", {}).get("results", [])
                if results and "url" in results[0]:
                    img = httpx.get(results[0]["url"], timeout=60)
                    with open(output_path, "wb") as f:
                        f.write(img.content)
                    return output_path
                raise RuntimeError("No image URL")
            elif st in ("FAILED", "CANCELED"):
                raise RuntimeError("Image gen " + st)
        raise TimeoutError("Timed out after " + str(timeout_seconds) + "s")

    def generate_video(self, prompt, output_path, resolution="720P", ratio="16:9", duration=5, model=None, timeout_seconds=300):
        import httpx, time
        api_key = settings.active_api_key
        model_name = model or "happyhorse-1.1-t2v"
        headers = {
            "Authorization": "Bearer " + api_key,
            "X-DashScope-Async": "enable",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model_name,
            "input": {"prompt": prompt},
            "parameters": {"resolution": resolution, "ratio": ratio, "duration": duration},
        }
        url = "https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis"
        resp = httpx.post(url, headers=headers, json=payload, timeout=30)
        data = resp.json()
        if "output" not in data or "task_id" not in data["output"]:
            raise RuntimeError("HappyHorse failed: " + data.get("message", "unknown"))
        task_id = data["output"]["task_id"]
        poll_h = {"Authorization": "Bearer " + api_key}
        start = time.time()
        while time.time() - start < timeout_seconds:
            time.sleep(5)
            surl = "https://dashscope-intl.aliyuncs.com/api/v1/tasks/" + task_id
            s = httpx.get(surl, headers=poll_h, timeout=15)
            sd = s.json()
            st = sd.get("output", {}).get("task_status", "UNKNOWN")
            if st == "SUCCEEDED":
                results = sd.get("output", {}).get("results", [])
                if results and "url" in results[0]:
                    vid = httpx.get(results[0]["url"], timeout=120)
                    with open(output_path, "wb") as f:
                        f.write(vid.content)
                    return output_path
                raise RuntimeError("No video URL")
            elif st in ("FAILED", "CANCELED"):
                raise RuntimeError("Video gen " + st)
        raise TimeoutError("Timed out after " + str(timeout_seconds) + "s")

    # ============================================================
    # EMBEDDINGS
    # ============================================================

    # ============================================================
    # EMBEDDINGS
    # ============================================================

    def embed(self, texts: list[str],
              model: Optional[str] = None) -> list[list[float]]:
        """Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed
            model: Embedding model name (default: text-embedding-v3)
        Returns:
            List of embedding vectors
        """
        model = model or settings.qwen_embedding_model
        resp = self.client.embeddings.create(
            model=model,
            input=texts,
        )
        return [item.embedding for item in resp.data]


# Singleton instance
qwen = QwenClient()
