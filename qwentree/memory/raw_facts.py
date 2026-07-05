"""Layer 3: Raw Facts — Ephemeral Context (Redis + TTL-based decay).

The lowest-priority memory tier. Stores transient context:
conversation logs, temporary data, recent interactions.
Auto-expires via TTL. No persistence across agent restarts.
"""

import json
import time
from typing import Optional

import redis as redis_py
from qwentree.core.config import settings


class RawFacts:
    """Ephemeral context store — auto-expires, lowest priority."""

    def __init__(self):
        self.client = redis_py.from_url(settings.redis_url, decode_responses=True)
        self._prefix = "confucius:raw:"

    def add(self, content: str, channel: str = "general",
            metadata: dict = None, ttl: int = None):
        """Store a raw fact with auto-expiry TTL."""
        if ttl is None:
            ttl = settings.raw_facts_ttl

        fact_id = f"{self._prefix}{channel}:{int(time.time() * 1000)}:{hash(content) % 10**6}"

        self.client.hset(fact_id, mapping={
            "content": content,
            "channel": channel,
            "metadata": json.dumps(metadata or {}),
            "created_at": str(time.time()),
        })
        self.client.expire(fact_id, ttl)

        # Maintain max items per channel (FIFO eviction)
        channel_key = f"{self._prefix}channel:{channel}"
        self.client.lpush(channel_key, fact_id)
        self.client.ltrim(channel_key, 0, settings.raw_facts_max_items - 1)
        self.client.expire(channel_key, ttl)

        return fact_id

    def retrieve(self, query: str, channel: Optional[str] = None,
                 max_results: int = None) -> list[dict]:
        """Retrieve recent raw facts, newest first."""
        if max_results is None:
            max_results = 10

        pattern = f"{self._prefix}{channel or '*'}:*"
        cursor = 0
        facts = []

        # Scan for matching keys
        while True:
            cursor, keys = self.client.scan(cursor, match=pattern, count=100)
            for key in keys:
                if self.client.exists(key):
                    data = self.client.hgetall(key)
                    age = time.time() - float(data.get("created_at", 0))
                    facts.append({
                        "content": data.get("content", ""),
                        "channel": data.get("channel", "general"),
                        "metadata": json.loads(data.get("metadata", "{}")),
                        "age_seconds": age,
                        "tier": "raw_fact",
                    })
            if cursor == 0:
                break

        # Sort by recency (newest first), limit results
        facts.sort(key=lambda f: f["age_seconds"])
        return facts[:max_results]

    def get_recent_session(self, limit: int = 20) -> list[dict]:
        """Get the most recent context messages."""
        return self.retrieve("", channel="session", max_results=limit)

    def clear_channel(self, channel: str):
        """Clear all facts in a channel."""
        pattern = f"{self._prefix}{channel}:*"
        cursor = 0
        while True:
            cursor, keys = self.client.scan(cursor, match=pattern)
            if keys:
                self.client.delete(*keys)
            if cursor == 0:
                break
