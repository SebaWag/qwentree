"""🔗 integrations/integrations — Integrations with Wagner Solutions ecosystem."""

import httpx
import os
from qwentree.core.config import settings


def shiva(query: str) -> dict:
    """Query SHIVA agent via API.

    Sends a query to the SHIVA agent system for processing.

    Args:
        query: Question or task for SHIVA
    Returns:
        dict with SHIVA's response
    """
    shiva_url = os.getenv("SHIVA_API_URL", "http://localhost:8001")
    shiva_key = os.getenv("SHIVA_API_KEY", "")

    try:
        resp = httpx.post(
            f"{shiva_url}/api/chat",
            headers={"Authorization": f"Bearer {shiva_key}"},
            json={"message": query},
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        return {
            "success": True,
            "response": data.get("response", ""),
            "agent": "SHIVA",
        }
    except httpx.HTTPError as e:
        return {"success": False, "error": f"SHIVA API error: {e}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def n8n(workflow_id: str, payload: dict = None) -> dict:
    """Execute an n8n workflow.

    Args:
        workflow_id: n8n workflow ID to execute
        payload: Optional data to pass to the workflow
    Returns:
        dict with workflow execution result
    """
    n8n_url = os.getenv("N8N_URL", "http://localhost:5678")
    n8n_key = os.getenv("N8N_API_KEY", "")

    try:
        resp = httpx.post(
            f"{n8n_url}/webhook/{workflow_id}",
            headers={"Authorization": f"Bearer {n8n_key}"},
            json=payload or {},
            timeout=120,
        )
        return {
            "success": True,
            "workflow_id": workflow_id,
            "status_code": resp.status_code,
            "response": resp.text[:2000],
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def academy(endpoint: str = "status") -> dict:
    """Check academy.wagnersolutionsai.com status.

    Args:
        endpoint: API endpoint to query (default: status)
    Returns:
        dict with academy status
    """
    try:
        resp = httpx.get(
            f"https://academy.wagnersolutionsai.com/api/{endpoint}",
            timeout=10,
        )
        return {
            "success": True,
            "status_code": resp.status_code,
            "response": resp.text[:1000],
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
