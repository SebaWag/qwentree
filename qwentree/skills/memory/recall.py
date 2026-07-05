"""🧠 memory/recall — Recall information from past sessions using 3-tier memory."""

from qwentree.memory.retrieval_pipeline import RetrievalPipeline


def recall(query: str, limit: int = 5) -> dict:
    """Search and recall information from all memory tiers.

    Searches across Mental Models (highest priority), Observations,
    and Raw Facts to find relevant information from past sessions.

    Args:
        query: What to search for
        limit: Maximum results per tier
    Returns:
        dict with recall results from all memory tiers
    """
    try:
        pipeline = RetrievalPipeline()
        result = pipeline.query(query)

        return {
            "success": True,
            "query": query,
            "mental_models": result.get("mental_models", []),
            "observations": result.get("observations", []),
            "raw_facts": result.get("raw_facts", []),
            "formatted_context": result.get("formatted_context", ""),
            "total_results": (
                len(result.get("mental_models", [])) +
                len(result.get("observations", [])) +
                len(result.get("raw_facts", []))
            ),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def search(query: str, tier: str = "all") -> dict:
    """Search a specific memory tier.

    Args:
        query: Search query
        tier: 'mental_models', 'observations', 'raw_facts', or 'all'
    """
    if tier == "mental_models":
        return {"success": True, "tier": "mental_models",
                "result": _search_mental_models(query)}
    elif tier == "observations":
        return {"success": True, "tier": "observations",
                "result": _search_observations(query)}
    elif tier == "raw_facts":
        return {"success": True, "tier": "raw_facts",
                "result": _search_raw_facts(query)}
    else:
        return recall(query)


def _search_mental_models(query: str) -> list:
    from qwentree.memory.mental_models import MentalModels
    mm = MentalModels()
    results = mm.retrieve(query)
    return [{"content": r.get("content", ""), "score": r.get("score", 0),
             "source": r.get("source", "")} for r in results]


def _search_observations(query: str) -> list:
    from qwentree.memory.observations import Observations
    obs = Observations()
    results = obs.search(query)
    return [{"content": r.get("content", ""), "category": r.get("category", ""),
             "confidence": r.get("confidence", 0)} for r in results]


def _search_raw_facts(query: str) -> list:
    from qwentree.memory.raw_facts import RawFacts
    rf = RawFacts()
    results = rf.search(query)
    return [{"content": r.get("content", ""), "channel": r.get("channel", ""),
             "timestamp": r.get("timestamp", "")} for r in results]
