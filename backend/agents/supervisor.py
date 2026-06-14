"""
backend/agents/supervisor.py

Supervisor Agent — Phase 0 of the LangGraph DAG.

Parses the job description using structured output (.with_structured_output())
to extract metadata that all downstream agents depend on:
  - company_name
  - role_title
  - hiring_manager
  - required_skills

Uses DeepSeek V4 Flash via OpenRouter (reliable structured extraction,
lower latency than larger models).
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableConfig
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import SystemMessage

from backend.agents.state import ApplicationState
from backend.llm.model import llm_writer
from backend.prompts.supervisor import SUPERVISOR_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# ─── Structured output schema ──────────────────────────────────────────────────

class SupervisorOutput(BaseModel):
    """Structured metadata extracted from the job description."""

    company_name: str = Field(
        description="The name of the hiring company."
    )
    role_title: str = Field(
        description="The exact job title as written in the posting."
    )
    hiring_manager: str = Field(
        default="",
        description="Full name of the hiring manager if explicitly mentioned; empty string otherwise.",
    )
    required_skills: list[str] = Field(
        default_factory=list,
        description="Top 8–12 required or preferred skills from the job description.",
    )


# ─── Agent node ───────────────────────────────────────────────────────────────

async def supervisor_agent(state: ApplicationState, config: RunnableConfig) -> dict[str, Any]:
    """
    LangGraph node: parse the JD and extract structured metadata.

    Reads:
        state["resume_text"]      — candidate's resume text
        state["job_description"]  — raw job description text

    Writes to state:
        company_name, role_title, hiring_manager, required_skills

    Returns:
        A dict with only the keys this agent is responsible for updating.
    """
    logger.info("Supervisor agent starting for run_id=%s", state.get("run_id"))

    resume_text = state.get("resume_text", "")
    job_description = state.get("job_description", "")

    if not job_description.strip():
        logger.error("Supervisor received empty job_description.")
        raise ValueError("job_description is required but was empty.")

    parser = JsonOutputParser(pydantic_object=SupervisorOutput)
    
    prompt_text = SUPERVISOR_SYSTEM_PROMPT.format(
        jd=job_description,
        resume=resume_text,
    )
    prompt_text += f"\n\n<format_instructions>\n{parser.get_format_instructions()}\n</format_instructions>"

    try:
        messages = [SystemMessage(content=prompt_text)]
        chain = llm_writer | parser
        result = await chain.ainvoke(messages, config)
        
        logger.info(
            "Supervisor extracted: company=%s, role=%s, skills=%d",
            result.get("company_name", ""),
            result.get("role_title", ""),
            len(result.get("required_skills", [])),
        )
    except Exception as exc:
        logger.error("Supervisor agent failed: %s", exc)
        raise

    return {
        "company_name": result.get("company_name", ""),
        "role_title": result.get("role_title", ""),
        "hiring_manager": result.get("hiring_manager", ""),
        "required_skills": result.get("required_skills", []),
    }
