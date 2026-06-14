"""
backend/agents/cover_letter.py

Cover Letter Agent.
"""
from __future__ import annotations

import logging
from langchain_core.messages import SystemMessage

from backend.agents.state import ApplicationState
from backend.llm.model import llm_writer
from backend.prompts.cover_letter import COVER_LETTER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

async def cover_letter_agent(state: ApplicationState) -> dict:
    run_id = state.get("run_id")
    logger.info("Cover Letter Agent starting for run_id=%s", run_id)
    
    prompt_text = COVER_LETTER_SYSTEM_PROMPT.format(
        tailored_resume=state.get("tailored_resume", ""),
        job_description=state.get("job_description", ""),
        research_brief=state.get("research_brief", ""),
        hiring_manager=state.get("hiring_manager", ""),
        company_name=state.get("company_name", "")
    )
    
    messages = [SystemMessage(content=prompt_text)]
    response = await llm_writer.ainvoke(messages)
    
    logger.info("Cover Letter Agent completed for run_id=%s", run_id)
    return {"cover_letter": response.content}
