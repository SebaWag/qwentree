"""Layer 2: Observations — Persistent Learnings (PostgreSQL + Time-index).

The middle-priority tier. Stores learnings, patterns, notes, and decisions
from previous agent sessions. Persists across sessions with recency weighting.
"""

import json
from datetime import datetime, timedelta
from typing import Optional

import psycopg2
import psycopg2.extras
from qwentree.core.config import settings


class Observations:
    """Persistent observation store — learns from past agent interactions."""

    def __init__(self):
        self._conn = None

    @property
    def conn(self):
        if self._conn is None or self._conn.closed:
            self._conn = psycopg2.connect(settings.postgres_dsn)
            self._init_db()
        return self._conn

    def _init_db(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS observations (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    category VARCHAR(100) DEFAULT 'general',
                    confidence FLOAT DEFAULT 1.0,
                    source_session VARCHAR(100),
                    metadata JSONB DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT NOW(),
                    accessed_at TIMESTAMP DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS idx_observations_category 
                    ON observations(category);
                CREATE INDEX IF NOT EXISTS idx_observations_created 
                    ON observations(created_at DESC);
            """)
        self.conn.commit()

    def add(self, content: str, category: str = "general",
            confidence: float = 1.0, source_session: str = None,
            metadata: dict = None):
        """Store a new observation/learning from an agent session."""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO observations (content, category, confidence, source_session, metadata)
                VALUES (%s, %s, %s, %s, %s)
            """, (content, category, confidence, source_session,
                  json.dumps(metadata or {})))
        self.conn.commit()

    def retrieve(self, query: str, category: Optional[str] = None,
                 max_results: int = None, recency_days: int = None) -> list[dict]:
        """Retrieve relevant observations with recency weighting."""
        if max_results is None:
            max_results = settings.observations_max_results
        if recency_days is None:
            recency_days = settings.observations_recency_days

        cutoff = datetime.utcnow() - timedelta(days=recency_days)

        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if category:
                cur.execute("""
                    SELECT *, 
                           EXTRACT(EPOCH FROM (NOW() - created_at)) / 86400.0 AS days_ago
                    FROM observations
                    WHERE created_at >= %s AND category = %s
                    ORDER BY confidence DESC, created_at DESC
                    LIMIT %s
                """, (cutoff, category, max_results))
            else:
                cur.execute("""
                    SELECT *,
                           EXTRACT(EPOCH FROM (NOW() - created_at)) / 86400.0 AS days_ago
                    FROM observations
                    WHERE created_at >= %s
                    ORDER BY confidence DESC, created_at DESC
                    LIMIT %s
                """, (cutoff, max_results))

            results = []
            for row in cur.fetchall():
                # Recency weight: 1.0 for today, decays to 0.0 after recency_days
                recency_weight = max(0.0, 1.0 - (row["days_ago"] / recency_days))
                priority_score = row["confidence"] * recency_weight
                results.append({
                    "content": row["content"],
                    "category": row["category"],
                    "confidence": row["confidence"],
                    "recency_weight": recency_weight,
                    "priority_score": priority_score,
                    "created_at": row["created_at"].isoformat(),
                    "tier": "observation",
                })
                # Update accessed_at
                self._touch(row["id"])

            return results

    def _touch(self, obs_id: int):
        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE observations SET accessed_at = NOW() WHERE id = %s",
                (obs_id,)
            )
        self.conn.commit()

    def close(self):
        if self._conn and not self._conn.closed:
            self._conn.close()
