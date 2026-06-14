"""
backend/agents/interview_prep.py

Interview Prep Agent.
"""
from __future__ import annotations

import logging
from langchain_core.messages import SystemMessage

from backend.agents.state import ApplicationState
from backend.llm.model import llm_writer
from backend.prompts.interview_prep import INTERVIEW_PREP_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

async def interview_prep_agent(state: ApplicationState) -> dict:
    run_id = state.get("run_id")
    logger.info("Interview Prep Agent starting for run_id=%s", run_id)
    
    prompt_text = INTERVIEW_PREP_SYSTEM_PROMPT.format(
        tailored_resume=state.get("tailored_resume", ""),
        job_description=state.get("job_description", ""),
        research_brief=state.get("research_brief", ""),
        role_title=state.get("role_title", ""),
        company_name=state.get("company_name", "")
    )
    
    messages = [SystemMessage(content=prompt_text)]
    response = await llm_writer.ainvoke(messages)
    
    logger.info("Interview Prep Agent completed for run_id=%s", run_id)
    return {"interview_qa": response.content}
