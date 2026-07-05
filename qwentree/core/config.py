"""QwenTree Configuration — Qwen Cloud Native Multimodal Agent.

Extends Confucius config with Qwen multimodal models for
vision, audio, video, code, and media generation.
All powered by QwenCloud unified API.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuration: Qwen Cloud for everything, fallback APIs for dev."""

    # === API Mode ===
    # "qwen" for Qwen Cloud (submission) | "fallback" for development
    api_mode: str = "fallback"

    # === Qwen Cloud (production / hackathon submission) ===
    qwen_api_key: Optional[str] = None
    qwen_base_url: str = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"

    # --- Text / Reasoning Models ---
    qwen_model: str = "qwen3.7-plus"           # General reasoning
    qwen_model_max: str = "qwen3.7-max"         # Deep reasoning (orchestrator)
    qwen_coder_model: str = "qwen-coder-plus"   # Code generation

    # --- Vision Models ---
    qwen_vl_model: str = "qwen-vl-max"          # Image/video analysis
    qwen_vl_plus: str = "qwen-vl-plus"          # Lighter vision

    # --- Audio Models ---
    qwen_audio_model: str = "qwen-audio"        # Speech-to-text
    qwen_tts_model: str = "cosyvoice-01"        # Text-to-speech (Alibaba)

    # --- Embeddings ---
    qwen_embedding_model: str = "text-embedding-v3"

    # --- Media Generation (QwenCloud native) ---
    qwen_image_model: str = "wan"               # Text-to-image (Wan)
    qwen_video_model: str = "wan-video"         # Text-to-video (Wan)

    # === Fallback API (development) ===
    fallback_api_key: Optional[str] = None
    fallback_base_url: Optional[str] = None
    fallback_model: Optional[str] = None

    # === Databases ===
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    postgres_dsn: str = "postgresql://qwentree:qwentree_secret@localhost:5433/qwentree"
    redis_url: str = "redis://localhost:6380/0"

    # === Memory Tiers ===
    mental_models_top_k: int = 5
    mental_models_score_threshold: float = 0.7
    observations_recency_days: int = 30
    observations_max_results: int = 10
    raw_facts_ttl: int = 3600
    raw_facts_max_items: int = 100

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def active_api_key(self) -> str:
        if self.api_mode == "qwen" and self.qwen_api_key:
            return self.qwen_api_key
        return self.fallback_api_key or ""

    @property
    def active_base_url(self) -> str:
        if self.api_mode == "qwen" and self.qwen_api_key:
            return self.qwen_base_url
        return self.fallback_base_url or "https://api.openai.com/v1"

    @property
    def active_model(self) -> str:
        if self.api_mode == "qwen" and self.qwen_api_key:
            return self.qwen_model
        return self.fallback_model or "gpt-4o"

    @property
    def is_qwen_mode(self) -> bool:
        return self.api_mode == "qwen" and bool(self.qwen_api_key)


settings = Settings()
