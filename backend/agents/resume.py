"""
backend/agents/resume.py

Resume Agent for the AI Job Co-Pilot.

This agent uses FAISS vector search to retrieve relevant sections of the
candidate's original resume based on the job description and required skills.
It then uses Qwen3-Coder (llm_coder) to rewrite the resume into an ATS-optimised,
tailored Markdown document.
"""

from __future__ import annotations

import logging

from langchain_core.messages import SystemMessage

from backend.agents.state import ApplicationState
from backend.llm.model import llm_coder
from backend.prompts.resume import RESUME_SYSTEM_PROMPT
from backend.tools.vector_search import retrieve_relevant_sections

logger = logging.getLogger(__name__)


async def resume_agent(state: ApplicationState) -> dict:
    """
    Retrieve relevant resume sections via FAISS and rewrite the resume.
    Uses llm_coder for structured rewriting.

    Args:
        state: The current ApplicationState.

    Returns:
        dict: Containing the `tailored_resume` (Markdown string).
    """
    run_id = state.get("run_id")
    logger.info("Resume Agent starting for run_id=%s", run_id)
    
    role_title = state.get("role_title", "")
    required_skills = state.get("required_skills", [])
    
    # Formulate a search query for the vector store
    # Combining the role title and required skills gives a strong semantic signal
    query = f"{role_title} {' '.join(required_skills)}"
    
    # Retrieve relevant past experience from FAISS
    retrieved_sections = await retrieve_relevant_sections(query, run_id)
    
    # Format the prompt
    prompt_text = RESUME_SYSTEM_PROMPT.format(
        resume_text=state.get("resume_text", ""),
        job_description=state.get("job_description", ""),
        required_skills=", ".join(required_skills),
        retrieved_sections=retrieved_sections,
    )
    
    # Qwen3-Coder handles the strict markdown generation
    # Use ainvoke as we are inside an async node and streaming is handled via astream_events at the API level
    messages = [SystemMessage(content=prompt_text)]
    
    logger.debug("Invoking llm_coder for resume generation...")
    response = await llm_coder.ainvoke(messages)
    
    logger.info("Resume Agent completed for run_id=%s", run_id)
    return {"tailored_resume": response.content}
