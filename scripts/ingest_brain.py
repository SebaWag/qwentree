#!/usr/bin/env python3
"""🧠 QwenTree Brain Ingestion — Poblar la memoria con nuestras sesiones.

Este script lee TODAS las sesiones pasadas de SHIVA y las clasifica
en la memoria jerárquica de 3 niveles:

  🏛️ MENTAL MODELS → Hechos canónicos, configuraciones, reglas
  📝 OBSERVATIONS  → Decisiones, patrones, aprendizajes
  📦 RAW FACTS     → Sesiones completas indexadas

Uso: python -m scripts.ingest_brain
"""

import os
import re
import json
import glob
from datetime import datetime
from pathlib import Path
from typing import Optional

# === CONFIGURACIÓN ===
SESSIONS_DIR = os.path.expanduser("~/shiva")
MEMORY_DIR = os.path.expanduser("~/shiva/qwentree/data/memory")

# Patrones para extraer información estructurada
PATTERNS = {
    "fecha": r"(\d{1,2}\s+de\s+\w+,\s+\d{4}|\d{4}-\d{2}-\d{2})",
    "url": r"https?://[^\s]+",
    "config": r"(?:timeout|puerto|host|api[_\s]key|token|url|endpoint)[=:]\s*['\"]?([^'\",\s\]]+)['\"]?",
    "comando": r"`([^`]+)`",
    "version": r"v?(\d+\.\d+\.\d+)",
    "tecnologia": r"(Python|JavaScript|TypeScript|React|FastAPI|Docker|PostgreSQL|Redis|ChromaDB|N8N|Traefik|Whisper|FFmpeg|Qwen|DeepSeek|Kimi|MiniMax|QwenCloud|Alibaba|Hetzner|Consensus|SHIVA|Swarm|Trinity|Confucius)",
    "error": r"(error|bug|issue|problema|fall[oó]|crash|timeout|exception)[^.]*\.",
    "solucion": r"(soluci[oó]n|fix|arregl[oó]|correg|resolv)[^.]*\.",
}


def extract_mental_models(text: str, source: str) -> list[dict]:
    """Extract canonical facts → Mental Models (highest priority)."""
    models = []

    # URLs de producción
    urls = re.findall(r"https?://[^\s\)\]]+", text)
    for url in urls:
        if any(d in url for d in [".com", ".app", ".io", ".cloud", ".ai"]):
            models.append({
                "content": f"URL de producción: {url}",
                "source": source,
                "tags": ["url", "production"],
                "priority": "high",
            })

    # Versiones de tecnologías
    for match in re.finditer(r"(Python|FastAPI|Node|React|Docker|PostgreSQL|Redis|ChromaDB)\s*(?:v|version)?\s*(\d+\.\d+(?:\.\d+)?)", text, re.IGNORECASE):
        models.append({
            "content": f"{match.group(1)} versión {match.group(2)}",
            "source": source,
            "tags": ["version", match.group(1).lower()],
            "priority": "high",
        })

    # Configuraciones
    for match in re.finditer(r"(?:configur[ae]|cambi[oó]|ajust[ae]|sete[ae]|modific[ae])(?:[^.]*?:)?\s*([^.]{10,200})\.", text, re.IGNORECASE):
        models.append({
            "content": match.group(1).strip(),
            "source": source,
            "tags": ["configuration"],
            "priority": "high",
        })

    return models


def extract_observations(text: str, source: str, fecha: str) -> list[dict]:
    """Extract decisions and learnings → Observations (medium priority)."""
    observations = []

    # Decisiones
    for match in re.finditer(r"(decidim|acordam|optam|elegim|definim)[^.]*\.", text, re.IGNORECASE):
        observations.append({
            "content": f"[{fecha}] {match.group(0).strip()}",
            "source": source,
            "category": "decision",
            "confidence": 0.9,
        })

    # Problemas y soluciones
    for match in re.finditer(r"(?:encontr[ae]|hab[ií]a|exist[íi]a|ocurr[íi]a)\s+(un\s+)?(error|bug|problema|issue)[^.]*\.", text, re.IGNORECASE):
        observations.append({
            "content": f"[{fecha}] Problema: {match.group(0).strip()}",
            "source": source,
            "category": "problem",
            "confidence": 0.8,
        })

    for match in re.finditer(r"(solucionam|arreglam|resolvim|fixe[ae]|corregim)[^.]*\.", text, re.IGNORECASE):
        observations.append({
            "content": f"[{fecha}] Solución: {match.group(0).strip()}",
            "source": source,
            "category": "solution",
            "confidence": 0.9,
        })

    # Tecnologías mencionadas
    techs = set(re.findall(
        r"(Python|JavaScript|TypeScript|React|FastAPI|Docker|PostgreSQL|Redis|ChromaDB|"
        r"N8N|Traefik|Whisper|FFmpeg|Qwen|DeepSeek|Kimi|MiniMax|"
        r"QwenCloud|Alibaba|Hetzner|Consensus|SHIVA|Swarm|Trinity|Confucius|"
        r"Wan|CosyVoice|Playwright|OpenAI|Claude|Anthropic|Palantir)",
        text, re.IGNORECASE
    ))
    for tech in sorted(techs):
        observations.append({
            "content": f"[{fecha}] Tecnología utilizada: {tech}",
            "source": source,
            "category": "technology",
            "confidence": 0.7,
        })

    return observations


def extract_raw_facts(text: str, source: str, fecha: str) -> list[dict]:
    """Extract session content → Raw Facts (lowest priority)."""
    facts = []

    # Session summary as raw fact
    facts.append({
        "content": f"Sesión {source}: {text[:500]}...",
        "source": source,
        "channel": "session",
        "fecha": fecha,
    })

    return facts


def ingest_session_file(filepath: str):
    """Process a single session file and extract all memory tiers."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"  ❌ Error leyendo {filepath}: {e}")
        return

    filename = os.path.basename(filepath)
    source = filename.replace(".md", "")

    # Extract date from filename or content
    date_match = re.search(r"(\d{4})(\d{2})(\d{2})", filename)
    if date_match:
        fecha = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"
    else:
        fecha = "unknown"

    print(f"\n  📄 Procesando: {filename}")
    print(f"     Fecha: {fecha}")

    # Extract all tiers
    mental = extract_mental_models(content, source)
    observations = extract_observations(content, source, fecha)
    raw = extract_raw_facts(content, source, fecha)

    print(f"     🏛️  Mental Models: {len(mental)}")
    print(f"     📝 Observations:  {len(observations)}")
    print(f"     📦 Raw Facts:     {len(raw)}")

    return {
        "source": source,
        "fecha": fecha,
        "mental_models": mental,
        "observations": observations,
        "raw_facts": raw,
    }


def store_in_chromadb(items: list[dict], tier: str):
    """Store items in ChromaDB for vector search."""
    try:
        from qwentree.memory.mental_models import MentalModels
        from qwentree.memory.observations import Observations
        from qwentree.memory.raw_facts import RawFacts

        stored = 0
        if tier == "mental_models":
            mm = MentalModels()
            for item in items:
                try:
                    mm.add_knowledge(
                        content=item["content"],
                        source=item["source"],
                        tags=item.get("tags", []),
                    )
                    stored += 1
                except Exception as e:
                    print(f"       ⚠️ Error storing mental model: {e}")
        elif tier == "observations":
            obs = Observations()
            for item in items:
                try:
                    obs.add_observation(
                        content=item["content"],
                        category=item.get("category", "general"),
                        confidence=item.get("confidence", 1.0),
                    )
                    stored += 1
                except Exception as e:
                    print(f"       ⚠️ Error storing observation: {e}")
        elif tier == "raw_facts":
            rf = RawFacts()
            for item in items:
                try:
                    rf.add_raw_fact(
                        content=item["content"],
                        channel=item.get("channel", "session"),
                    )
                    stored += 1
                except Exception as e:
                    print(f"       ⚠️ Error storing raw fact: {e}")

        return stored
    except ImportError as e:
        print(f"       ⚠️ No se pudo importar módulo de memoria: {e}")
        return 0
    except Exception as e:
        print(f"       ⚠️ Error storing in {tier}: {e}")
        return 0


def store_local_backup(all_data: list[dict]):
    """Store a local JSON backup of the brain."""
    os.makedirs(MEMORY_DIR, exist_ok=True)
    backup_path = os.path.join(MEMORY_DIR, "brain_sessions.json")

    # Flatten all items
    brain = {
        "last_updated": datetime.now().isoformat(),
        "total_sessions": len(all_data),
        "mental_models": [],
        "observations": [],
        "raw_facts": [],
    }

    for session in all_data:
        brain["mental_models"].extend(session["mental_models"])
        brain["observations"].extend(session["observations"])
        brain["raw_facts"].extend(session["raw_facts"])

    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump(brain, f, ensure_ascii=False, indent=2)

    print(f"\n     💾 Backup guardado: {backup_path}")
    return brain


def print_brain_statistics(brain: dict):
    """Print beautiful statistics of the ingested brain."""
    print()
    print("=" * 60)
    print("  🧠 QWENTREE BRAIN — ESTADÍSTICAS DE INGESTIÓN")
    print("=" * 60)
    print(f"\n  📚 Sesiones procesadas:    {brain['total_sessions']}")
    print(f"  🏛️  Mental Models:          {len(brain['mental_models'])}")
    print(f"  📝 Observations:           {len(brain['observations'])}")
    print(f"  📦 Raw Facts:              {len(brain['raw_facts'])}")
    print(f"  📊 TOTAL:                  {len(brain['mental_models']) + len(brain['observations']) + len(brain['raw_facts'])}")

    # Count by category
    from collections import Counter
    cats = Counter(o.get("category", "general") for o in brain["observations"])
    if cats:
        print(f"\n  📊 Observations por categoría:")
        for cat, count in cats.most_common():
            print(f"     • {cat}: {count}")
    print("=" * 60)


def ingest(force_reindex: bool = False):
    """Main ingestion function.

    Args:
        force_reindex: If True, clear existing memory before re-ingesting
    """
    print()
    print("=" * 60)
    print("  🧠 QWENTREE BRAIN INGESTION")
    print("  Poblando memoria con sesiones pasadas...")
    print("=" * 60)

    # Find all session files
    session_files = sorted(glob.glob(os.path.join(SESSIONS_DIR, "SESSION_NOTE_*.md")))
    session_files += sorted(glob.glob(os.path.join(SESSIONS_DIR, "session_*.md")))

    # Also look for session notes in subdirectories
    session_files += sorted(glob.glob(os.path.join(SESSIONS_DIR, "**/SESSION_NOTE_*.md"), recursive=True))

    # Remove duplicates
    session_files = sorted(set(session_files))

    print(f"\n  📁 Buscando en: {SESSIONS_DIR}")
    print(f"  📄 Archivos encontrados: {len(session_files)}")
    print()

    if not session_files:
        print("  ⚠️  No se encontraron archivos de sesión.")
        print("  💡 Crea archivos SESSION_NOTE_*.md en ~/shiva/")
        return

    # Clear existing memory if force_reindex
    if force_reindex:
        print("  🔄 Force reindex: limpiando memoria existente...")
        # We'll just overwrite, the stores handle upserts

    # Process each session
    all_data = []
    total_mental = 0
    total_obs = 0
    total_raw = 0

    for filepath in session_files:
        result = ingest_session_file(filepath)
        if result:
            all_data.append(result)

    # Store locally first
    brain = store_local_backup(all_data)

    # Now try to store in actual memory databases
    print("\n  💾 Almacenando en bases de datos de memoria...")
    print()

    for session in all_data:
        print(f"  → {session['source']}")

        # Mental Models (ChromaDB)
        stored = store_in_chromadb(session["mental_models"], "mental_models")
        total_mental += stored
        if stored > 0:
            print(f"    ✅ {stored} mental models stored")

        # Observations (PostgreSQL)
        stored = store_in_chromadb(session["observations"], "observations")
        total_obs += stored
        if stored > 0:
            print(f"    ✅ {stored} observations stored")

        # Raw Facts (Redis)
        stored = store_in_chromadb(session["raw_facts"], "raw_facts")
        total_raw += stored
        if stored > 0:
            print(f"    ✅ {stored} raw facts stored")

    # Update brain stats with actual stored counts
    if total_mental > 0:
        brain["mental_models_stored"] = total_mental
    if total_obs > 0:
        brain["observations_stored"] = total_obs
    if total_raw > 0:
        brain["raw_facts_stored"] = total_raw

    # Final statistics
    print_brain_statistics(brain)

    # Save updated stats
    stats_path = os.path.join(MEMORY_DIR, "brain_stats.json")
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump({
            "last_ingested": datetime.now().isoformat(),
            "total_sessions": brain["total_sessions"],
            "mental_models": len(brain["mental_models"]),
            "observations": len(brain["observations"]),
            "raw_facts": len(brain["raw_facts"]),
            "mental_models_stored": total_mental,
            "observations_stored": total_obs,
            "raw_facts_stored": total_raw,
        }, f, indent=2)

    print(f"\n  ✅ ¡Cerebro listo!")
    print(f"  💡 Ahora QwenTree recuerda {brain['total_sessions']} sesiones de trabajo.")
    print()


if __name__ == "__main__":
    import sys
    force = "--force" in sys.argv or "--reindex" in sys.argv
    ingest(force_reindex=force)
