"""
backend/agents/tracker.py
Saves outputs to MongoDB and triggers file export.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from backend.agents.state import ApplicationState
from backend.db.collections import outputs_collection
from backend.tools.file_export import export_outputs
from backend.tools.email import send_outreach_email

logger = logging.getLogger(__name__)

async def tracker_node(state: ApplicationState) -> dict:
    run_id = state.get("run_id")
    logger.info("Tracker node starting for run_id=%s", run_id)
    
    # Export files (docx)
    await export_outputs(state)

    # Send email draft if configured
    outreach_draft = state.get("outreach_draft", "")
    company_name = state.get("company_name", "Unknown Company")
    role_title = state.get("role_title", "Unknown Role")
    if outreach_draft:
        await send_outreach_email(company_name, role_title, outreach_draft)

    now = datetime.now(timezone.utc)
    # Save outputs to MongoDB
    outputs = [
        {"output_type": "tailored_resume", "content": state.get("tailored_resume", "")},
        {"output_type": "cover_letter", "content": state.get("cover_letter", "")},
        {"output_type": "interview_qa", "content": state.get("interview_qa", "")},
        {"output_type": "outreach_draft", "content": state.get("outreach_draft", "")},
        {"output_type": "research_brief", "content": state.get("research_brief", "")},
    ]

    docs = []
    for out in outputs:
        if out["content"]:
            docs.append({
                "application_id": run_id,
                "output_type": out["output_type"],
                "content": out["content"],
                "approved": False,
                "created_at": now
            })
            
    if docs:
        await outputs_collection.insert_many(docs)
    
    logger.info("Tracker node completed for run_id=%s", run_id)
    return {}
