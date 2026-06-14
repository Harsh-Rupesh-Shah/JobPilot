"""
backend/api/routes/stream.py

GET /stream/{run_id}

Server-Sent Events endpoint. Streams LangGraph astream_events() output
token-by-token to the frontend, multiplexed by agent name.

SSE message format:
    data: {"agent": "research", "token": "..."}
    data: {"agent": "supervisor", "token": "..."}
    data: {"event": "complete", "research_brief": "..."}
    data: {"event": "error", "message": "..."}

Authentication: the EventSource API does not support custom headers, so the
JWT access token is passed as a query parameter (?token=...) and validated here.
"""

from __future__ import annotations

import json
import logging
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from backend.agents.graph import graph
from backend.agents.state import ApplicationState
from backend.auth.jwt import decode_token
from backend.api.stream_manager import stream_manager

logger = logging.getLogger(__name__)
router = APIRouter()


# ─── Auth helper ──────────────────────────────────────────────────────────────

async def _get_user_from_token(token: str) -> str:
    """
    Validate a JWT access token passed as a query parameter.

    Args:
        token: Raw JWT string from the ?token= query param.

    Returns:
        The user_id (sub claim) from the token.

    Raises:
        HTTPException 401 if the token is missing, malformed, or expired.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token.",
        )
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub", "")
        if not user_id:
            raise ValueError("Missing sub claim in token.")
        return user_id
    except Exception as exc:
        logger.warning("SSE auth failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )


# ─── SSE event generator ──────────────────────────────────────────────────────

async def _event_generator(run_id: str) -> AsyncGenerator[str, None]:
    """
    Subscribe to LangGraph astream_events() and yield SSE-formatted messages.

    Yields one SSE message per LLM token (on_llm_new_token events), plus a
    final 'complete' event with the full research_brief when the graph ends.

    Args:
        run_id: The LangGraph thread_id for this run.

    Yields:
        SSE data strings (each ending with double newline as per SSE spec).
    """
    config = {"configurable": {"thread_id": run_id}}

    try:
        # Subscribe to the pubsub manager
        queue = stream_manager.subscribe(run_id)
        
        while True:
            # We don't want to block indefinitely if the backend shuts down
            # but SSE streams are long-lived, so we just await.
            event = await queue.get()
            
            event_name: str = event.get("event", "")
            
            if event_name == "GRAPH_END":
                break
                
            if event_name == "error":
                error_payload = json.dumps({"event": "error", "message": event.get("message", "Unknown error")})
                yield f"data: {error_payload}\n\n"
                continue

            metadata: dict = event.get("metadata", {})
            agent_name: str = metadata.get("langgraph_node", "unknown")

            # ── Token-by-token streaming ───────────────────────────────────────
            if event_name == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk")
                if chunk and hasattr(chunk, "content") and chunk.content:
                    token = chunk.content
                    payload = json.dumps({"agent": agent_name, "token": token})
                    yield f"data: {payload}\n\n"

            # ── Graph run ended cleanly ────────────────────────────────────────
            elif event_name == "on_chain_end" and agent_name == "LangGraph":
                # Read final state to get the research_brief
                try:
                    snapshot = graph.get_state(config)
                    research_brief = ""
                    if snapshot and snapshot.values:
                        research_brief = snapshot.values.get("research_brief", "")

                    payload = json.dumps({
                        "event": "complete",
                        "research_brief": research_brief,
                    })
                    yield f"data: {payload}\n\n"
                except Exception as state_exc:
                    logger.warning("Could not read final state: %s", state_exc)
                    yield f"data: {json.dumps({'event': 'complete'})}\n\n"
    except asyncio.CancelledError:
        logger.info("SSE client disconnected for run_id=%s", run_id)
    except Exception as exc:
        logger.error("SSE stream error for run_id=%s: %s", run_id, exc)
        error_payload = json.dumps({"event": "error", "message": str(exc)})
        yield f"data: {error_payload}\n\n"
    finally:
        stream_manager.unsubscribe(run_id, queue)


# ─── Route ────────────────────────────────────────────────────────────────────

@router.get("/{run_id}")
async def stream_run(
    run_id: str,
    token: str,
    request: Request,
) -> StreamingResponse:
    """
    Stream LangGraph execution events for a run via Server-Sent Events.

    The frontend opens this as an EventSource connection and receives one
    SSE message per LLM token, terminated by a 'complete' event.

    Query params:
        token (str): JWT access token (required — EventSource cannot set headers).
    """
    await _get_user_from_token(token)
    logger.info("SSE connection opened for run_id=%s", run_id)

    return StreamingResponse(
        _event_generator(run_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # disable nginx buffering for SSE
        },
    )
