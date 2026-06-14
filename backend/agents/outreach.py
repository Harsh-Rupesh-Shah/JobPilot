"""
backend/agents/outreach.py

Outreach Agent.
"""
from __future__ import annotations

import logging
from langchain_core.messages import SystemMessage

from backend.agents.state import ApplicationState
from backend.llm.model import llm_writer
from backend.prompts.outreach import OUTREACH_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

async def outreach_agent(state: ApplicationState) -> dict:
    run_id = state.get("run_id")
    logger.info("Outreach Agent starting for run_id=%s", run_id)
    
    prompt_text = OUTREACH_SYSTEM_PROMPT.format(
        tailored_resume=state.get("tailored_resume", ""),
        job_description=state.get("job_description", ""),
        research_brief=state.get("research_brief", ""),
        hiring_manager=state.get("hiring_manager", ""),
        company_name=state.get("company_name", ""),
        role_title=state.get("role_title", "")
    )
    
    messages = [SystemMessage(content=prompt_text)]
    response = await llm_writer.ainvoke(messages)
    
    logger.info("Outreach Agent completed for run_id=%s", run_id)
    return {"outreach_draft": response.content}
