"""Retrieval Pipeline — Hierarchical Memory Orchestrator.

Queries all 3 memory tiers in parallel, then ranks and prioritizes results:
1. Mental Models (highest priority — canonical knowledge)
2. Observations (medium priority — persistent learnings)
3. Raw Facts (lowest priority — ephemeral context)

Returns a consolidated, priority-ranked context for the agent.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

from qwentree.memory.mental_models import MentalModels
from qwentree.memory.observations import Observations
from qwentree.memory.raw_facts import RawFacts


# Priority weights for each tier
TIER_WEIGHTS = {
    "mental_model": 1.0,  # Highest — canonical truth
    "observation": 0.6,   # Medium — learned patterns
    "raw_fact": 0.3,      # Lowest — ephemeral context
}


class RetrievalPipeline:
    """Orchestrates multi-tier memory retrieval with priority ranking."""

    def __init__(self):
        self.mental_models = MentalModels()
        self.observations = Observations()
        self.raw_facts = RawFacts()

    def query(self, query: str, category: Optional[str] = None,
              max_total: int = 15) -> dict:
        """Query all memory tiers in parallel, return ranked context."""
        results = {"context": [], "tiers_used": [], "stats": {}}

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(self._query_mental_models, query): "mental_models",
                executor.submit(self._query_observations, query, category): "observations",
                executor.submit(self._query_raw_facts, query): "raw_facts",
            }

            for future in as_completed(futures):
                tier_name = futures[future]
                try:
                    tier_results = future.result()
                    results["context"].extend(tier_results)
                    results["tiers_used"].append(tier_name)
                    results["stats"][tier_name] = len(tier_results)
                except Exception as e:
                    results["stats"][tier_name] = f"error: {str(e)}"

        # Priority ranking: sort by (tier_weight * recency_score)
        for item in results["context"]:
            tier = item.get("tier", "raw_fact")
            weight = TIER_WEIGHTS.get(tier, 0.3)

            # Observations ya tienen priority_score (confidence * recency)
            if "priority_score" in item and item["priority_score"]:
                score = item["priority_score"]
            else:
                # Mental Models y Raw Facts: convertir distancia a similitud
                # ChromaDB: menor distancia = más similar
                raw_score = item.get("score", 0) or 0
                similarity = item.get("similarity", 1.0 - min(raw_score, 1.0))
                score = similarity

            item["rank"] = weight * max(0, score)

        results["context"].sort(key=lambda x: x.get("rank", 0), reverse=True)
        results["context"] = results["context"][:max_total]

        # Build consolidated context string for the LLM
        results["formatted_context"] = self._format_context(results["context"])

        return results

    def add_mental_model(self, content: str, source: str, tags: list[str] = None):
        """Add canonical knowledge to the Mental Models tier."""
        return self.mental_models.add_knowledge(content, source, tags)

    def add_observation(self, content: str, category: str = "general",
                        confidence: float = 1.0, source_session: str = None,
                        metadata: dict = None):
        """Store a learning/observation from an agent session."""
        return self.observations.add(content, category, confidence,
                                     source_session, metadata)

    def add_raw_fact(self, content: str, channel: str = "general",
                     metadata: dict = None):
        """Store ephemeral context."""
        return self.raw_facts.add(content, channel, metadata)

    def _query_mental_models(self, query: str) -> list:
        return self.mental_models.retrieve(query)

    def _query_observations(self, query: str, category: Optional[str]) -> list:
        return self.observations.retrieve(query, category=category)

    def _query_raw_facts(self, query: str) -> list:
        return self.raw_facts.retrieve(query)

    def _format_context(self, items: list[dict]) -> str:
        """Format retrieved items into a consolidated context string."""
        if not items:
            return "No relevant context found in memory."

        lines = ["=== HIERARCHICAL MEMORY CONTEXT ===\n"]

        for item in items:
            tier = item.get("tier", "unknown")
            tier_label = {
                "mental_model": "🏛️ MENTAL MODEL (canonical)",
                "observation": "📝 OBSERVATION (learned)",
                "raw_fact": "📦 RAW FACT (ephemeral)",
            }.get(tier, tier)

            lines.append(f"[{tier_label}]")
            lines.append(f"  {item['content']}")
            if item.get("metadata"):
                lines.append(f"  metadata: {item['metadata']}")
            lines.append("")

        return "\n".join(lines)
