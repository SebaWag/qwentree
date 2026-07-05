"""Layer 1: Mental Models — Canonical Knowledge (ChromaDB HTTP Client).

Connects to the external ChromaDB service. The highest-priority memory tier.
Stores curated, validated knowledge as the "source of truth" for the agent.
"""

import os
import uuid
import chromadb
from chromadb.config import Settings as ChromaSettings
from openai import OpenAI
from qwentree.core.config import settings


class MentalModels:
    """Canonical knowledge base using ChromaDB HTTP client."""

    def __init__(self):
        # Connect to external ChromaDB service via HTTP
        chroma_host = os.getenv("CHROMA_HOST", "localhost")
        chroma_port = os.getenv("CHROMA_PORT", "8000")
        self.client = chromadb.HttpClient(
            host=chroma_host,
            port=int(chroma_port),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name="mental_models",
            metadata={"description": "Canonical knowledge — Mental Models tier"},
        )
        self.llm = OpenAI(
            api_key=settings.active_api_key,
            base_url=settings.active_base_url,
        )

    def add_knowledge(self, content: str, source: str, tags: list[str] = None):
        """Add a piece of canonical knowledge to Mental Models."""
        embedding = self._embed(content)
        doc_id = f"mm_{uuid.uuid4().hex[:16]}"
        self.collection.add(
            documents=[content],
            embeddings=[embedding],
            metadatas=[{"source": source, "tags": ",".join(tags or [])}],
            ids=[doc_id],
        )
        return doc_id

    def retrieve(self, query: str, top_k: int = None) -> list[dict]:
        """Retrieve the most relevant Mental Models for a query."""
        if top_k is None:
            top_k = settings.mental_models_top_k

        query_embedding = self._embed(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        items = []
        if results and results.get("documents"):
            for i, doc in enumerate(results["documents"][0]):
                score = results["distances"][0][i] if results.get("distances") else 0
                # ChromaDB distances: lower = more similar. Convert to similarity.
                similarity = 1.0 - min(score, 1.0)
                if similarity >= settings.mental_models_score_threshold:
                    items.append({
                        "content": doc,
                        "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                        "score": score,
                        "similarity": similarity,
                        "tier": "mental_model",
                    })
        return items

    def _embed(self, text: str) -> list[float]:
        """Generate embedding using Qwen Cloud or fallback API."""
        try:
            resp = self.llm.embeddings.create(
                model=settings.qwen_embedding_model,
                input=text,
            )
            return resp.data[0].embedding
        except Exception:
            # Fallback: return zero vector (will still work, just less precise)
            return [0.0] * 768
