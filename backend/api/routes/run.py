"""
backend/api/routes/run.py

Handles starting a new co-pilot run, polling its status, and submitting
human-in-the-loop approval.

POST /run         — Invokes the LangGraph graph in a background thread
GET  /status/{id} — Reads graph state from the MongoDB checkpointer
POST /approve/{id}— (stub — will be activated when hitl.py is added)
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional
import os

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel
from langgraph.types import Command

from backend.agents.graph import graph
from backend.agents.state import ApplicationState
from backend.auth.dependencies import get_current_user
from backend.auth.models import UserResponse
from backend.config import settings
from backend.db.collections import applications_collection
from backend.parsers.resume_parser import extract_text_from_file
from backend.api.stream_manager import stream_manager

logger = logging.getLogger(__name__)
router = APIRouter()


# ─── Request / response models ────────────────────────────────────────────────

class RunRequest(BaseModel):
    """Body for POST /run."""

    job_url: Optional[str] = None
    job_description: Optional[str] = None
    resume_id: str             # ID of the previously uploaded resume


class RunResponse(BaseModel):
    """Response from POST /run."""

    run_id: str


class RunStatusResponse(BaseModel):
    """Response from GET /status/{run_id}."""

    run_id: str
    status: str                     # running | complete | failed
    current_agent: Optional[str] = None
    research_brief: Optional[str] = None
    interrupt_payload: Optional[dict] = None


class ApproveRequest(BaseModel):
    """Body for POST /approve/{run_id} — will be used when HITL node is added."""

    tailored_resume: str
    cover_letter: str
    outreach_draft: str
    interview_qa: str


# ─── Background task: run the graph ───────────────────────────────────────────

async def _invoke_graph(run_id: str, initial_state: dict[str, Any]) -> None:
    """
    Run the LangGraph graph asynchronously in a background task.

    Updates the application record in MongoDB on completion or failure.
    """
    config = {"configurable": {"thread_id": run_id}}
    try:
        logger.info("Graph invocation starting for run_id=%s", run_id)
        
        # Use astream_events to broadcast events while the graph runs
        async for event in graph.astream_events(initial_state, config, version="v2"):
            await stream_manager.broadcast(run_id, event)
            
        # Send sentinel
        await stream_manager.broadcast(run_id, {"event": "GRAPH_END"})

        logger.info("Graph invocation completed/paused for run_id=%s", run_id)
        
        # Check if the graph is paused or fully complete
        snapshot = graph.get_state(config)
        if snapshot.next:
            status_val = "pending_approval"
        else:
            status_val = "complete"

        update_dict = {
            "status": status_val, 
            "updated_at": datetime.now(timezone.utc)
        }
        if snapshot and snapshot.values:
            update_dict["company"] = snapshot.values.get("company_name", "Unknown Company")
            update_dict["role"] = snapshot.values.get("role_title", "Unknown Role")

        await applications_collection.update_one(
            {"_id": run_id},
            {"$set": update_dict},
        )
    except Exception as exc:
        logger.error("Graph invocation failed for run_id=%s: %s", run_id, exc)
        await applications_collection.update_one(
            {"_id": run_id},
            {
                "$set": {
                    "status": "failed",
                    "error": str(exc),
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )
        await stream_manager.broadcast(run_id, {"event": "error", "message": str(exc)})
        await stream_manager.broadcast(run_id, {"event": "GRAPH_END"})


async def _resume_graph(run_id: str, user_edits: dict) -> None:
    """
    Resume the LangGraph graph asynchronously after HITL approval.
    """
    config = {"configurable": {"thread_id": run_id}}
    try:
        logger.info("Resuming graph for run_id=%s", run_id)
        
        # We invoke graph with Command(resume=user_edits)
        async for _ in graph.astream_events(Command(resume=user_edits), config, version="v2"):
            # Tracker node doesn't stream LLM tokens, so we can just wait for it to finish.
            pass

        # Graph is truly complete now
        snapshot = graph.get_state(config)
        update_dict = {"status": "complete", "updated_at": datetime.now(timezone.utc)}
        if snapshot and snapshot.values:
            update_dict["interview_qa"] = snapshot.values.get("interview_qa", "")
            update_dict["hiring_manager"] = snapshot.values.get("hiring_manager", "")
            update_dict["outreach_draft"] = snapshot.values.get("outreach_draft", "")
            update_dict["company"] = snapshot.values.get("company_name", "Unknown Company")
            update_dict["role"] = snapshot.values.get("role_title", "Unknown Role")

        await applications_collection.update_one(
            {"_id": run_id},
            {"$set": update_dict},
        )
        logger.info("Graph resumed and completed for run_id=%s", run_id)
    except Exception as exc:
        logger.error("Graph resume failed for run_id=%s: %s", run_id, exc)
        await applications_collection.update_one(
            {"_id": run_id},
            {
                "$set": {
                    "status": "failed",
                    "error": str(exc),
                    "updated_at": datetime.now(timezone.utc),
                }
            },
        )


# ─── Routes ───────────────────────────────────────────────────────────────────

@router.post("/run", response_model=RunResponse)
async def start_run(
    req: RunRequest,
    background_tasks: BackgroundTasks,
    current_user: UserResponse = Depends(get_current_user),
) -> RunResponse:
    """
    Start a new co-pilot run.

    Validates inputs, creates a run record in MongoDB, and launches the
    LangGraph graph in a background task so the response is returned immediately.
    """
    if not req.job_description and not req.job_url:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Either job_description or job_url must be provided.",
        )

    if not req.resume_id.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="resume_id is required.",
        )

    # Locate and read the uploaded resume file
    resume_text = ""
    for ext in ["pdf", "docx"]:
        file_path = os.path.join(settings.UPLOAD_DIR, f"{req.resume_id}.{ext}")
        if os.path.exists(file_path):
            try:
                resume_text = await extract_text_from_file(file_path, ext)
                break
            except Exception as e:
                logger.warning("Failed to extract text from %s: %s", file_path, e)
    
    if not resume_text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume file not found or could not be parsed.",
        )

    run_id = f"run_{uuid.uuid4().hex}"
    user_id: str = current_user.user_id
    now = datetime.now(timezone.utc)

    # Build initial graph state
    initial_state: dict[str, Any] = {
        "resume_text": resume_text,
        "job_description": req.job_description or "",
        "job_url": req.job_url or "",
        "company_name": "",
        "role_title": "",
        "hiring_manager": "",
        "required_skills": [],
        "research_brief": "",
        "tailored_resume": "",
        "cover_letter": "",
        "interview_qa": "",
        "outreach_draft": "",
        "messages": [],
        "run_id": run_id,
        "user_id": user_id,
        "timestamp": now.isoformat(),
    }

    # Persist the run record before launching so status polling works immediately
    await applications_collection.insert_one(
        {
            "_id": run_id,
            "run_id": run_id,
            "user_id": user_id,
            "job_url": req.job_url or "",
            "job_description": req.job_description or "",
            "status": "running",
            "created_at": now,
            "updated_at": now,
        }
    )

    # Launch graph in background (non-blocking)
    background_tasks.add_task(_invoke_graph, run_id, initial_state)
    logger.info("Run %s created for user %s", run_id, user_id)

    return RunResponse(run_id=run_id)


@router.get("/status/{run_id}", response_model=RunStatusResponse)
async def get_run_status(
    run_id: str,
    current_user: UserResponse = Depends(get_current_user),
) -> RunStatusResponse:
    """
    Poll the current status of a co-pilot run.

    Reads the persisted application record from MongoDB and, if the run is
    complete, also reads the final graph state from the LangGraph checkpointer
    to return the research_brief.
    """
    # Verify the run exists and belongs to this user
    record = await applications_collection.find_one(
        {"_id": run_id, "user_id": current_user.user_id}
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Run '{run_id}' not found.",
        )

    run_status: str = record.get("status", "running")
    research_brief: Optional[str] = None

    # If complete, read the final graph state from the checkpointer
    if run_status == "complete":
        try:
            config = {"configurable": {"thread_id": run_id}}
            state_snapshot = graph.get_state(config)
            if state_snapshot and state_snapshot.values:
                research_brief = state_snapshot.values.get("research_brief")
        except Exception as exc:
            logger.warning("Could not read graph state for run_id=%s: %s", run_id, exc)

    return RunStatusResponse(
        run_id=run_id,
        status=run_status,
        research_brief=research_brief,
    )


@router.post("/approve/{run_id}")
async def approve_run(
    run_id: str,
    req: ApproveRequest,
    background_tasks: BackgroundTasks,
    current_user: UserResponse = Depends(get_current_user),
) -> dict[str, str]:
    """
    Submit human-in-the-loop approval to resume the graph.
    """
    # Verify the run exists and belongs to this user
    record = await applications_collection.find_one(
        {"_id": run_id, "user_id": current_user.user_id}
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Run '{run_id}' not found.",
        )

    # Update status to running again, since it was interrupted
    await applications_collection.update_one(
        {"_id": run_id},
        {"$set": {"status": "running", "updated_at": datetime.now(timezone.utc)}},
    )

    # Resume graph in background task
    background_tasks.add_task(_resume_graph, run_id, req.model_dump())
    
    return {"status": "accepted", "message": "Run resumed."}
