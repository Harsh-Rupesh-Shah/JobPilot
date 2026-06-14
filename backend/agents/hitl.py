"""
backend/agents/hitl.py

Human-in-the-Loop node. Uses LangGraph's interrupt() to pause the graph execution
and wait for human approval of the generated drafts.
"""
from __future__ import annotations

import logging
from langgraph.types import interrupt
from backend.agents.state import ApplicationState

logger = logging.getLogger(__name__)

def hitl_node(state: ApplicationState) -> dict:
    run_id = state.get("run_id")
    logger.info("HITL checkpoint reached for run_id=%s. Pausing graph...", run_id)
    
    # Pause the graph. The returned `user_edits` will be the data passed to Command(resume=...)
    user_edits = interrupt({
        "message": "Awaiting human approval.",
        "outputs": {
            "tailored_resume": state.get("tailored_resume", ""),
            "cover_letter": state.get("cover_letter", ""),
            "interview_qa": state.get("interview_qa", ""),
            "outreach_draft": state.get("outreach_draft", ""),
        }
    })
    
    logger.info("HITL checkpoint resumed for run_id=%s with user edits.", run_id)
    
    # Return the user edits so they overwrite the state
    return {
        "tailored_resume": user_edits.get("tailored_resume", state.get("tailored_resume", "")),
        "cover_letter": user_edits.get("cover_letter", state.get("cover_letter", "")),
        "outreach_draft": user_edits.get("outreach_draft", state.get("outreach_draft", "")),
    }

