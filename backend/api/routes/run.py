from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.auth.dependencies import get_current_user
from backend.auth.models import UserResponse

router = APIRouter()

class RunRequest(BaseModel):
    job_url: Optional[str] = None
    job_description: Optional[str] = None
    resume_id: str

class RunResponse(BaseModel):
    run_id: str

class RunStatusResponse(BaseModel):
    run_id: str
    status: str # 'running', 'pending_approval', 'complete', 'failed'
    current_agent: Optional[str] = None
    interrupt_payload: Optional[dict] = None

class ApproveRequest(BaseModel):
    tailored_resume: str
    cover_letter: str
    outreach_draft: str

@router.post("/run", response_model=RunResponse)
async def start_run(
    req: RunRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Initializes a new LangGraph application run thread.
    Returns the thread ID (run_id).
    """
    # Stub implementation. Will wire to graph.py later.
    import uuid
    return RunResponse(run_id=f"run_{uuid.uuid4().hex[:8]}")

@router.get("/status/{run_id}", response_model=RunStatusResponse)
async def get_run_status(
    run_id: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Polls the current state of the LangGraph execution.
    """
    # Stub implementation.
    return RunStatusResponse(
        run_id=run_id,
        status="running",
        current_agent="research"
    )

@router.post("/approve/{run_id}")
async def approve_run(
    run_id: str,
    req: ApproveRequest,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Submits human-in-the-loop edits to resume the graph.
    """
    # Stub implementation
    return {"status": "resumed"}
