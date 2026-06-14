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

from backend.agents.state import ApplicationState
from backend.llm.model import get_structured_llm
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

def supervisor_agent(state: ApplicationState, config: RunnableConfig) -> dict[str, Any]:
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

    prompt = SUPERVISOR_SYSTEM_PROMPT.format(
        jd=job_description,
        resume=resume_text,
    )

    try:
        structured_llm = get_structured_llm(SupervisorOutput)
        result: SupervisorOutput = structured_llm.invoke(prompt, config)
        logger.info(
            "Supervisor extracted: company=%s, role=%s, skills=%d",
            result.company_name,
            result.role_title,
            len(result.required_skills),
        )
    except Exception as exc:
        logger.error("Supervisor agent failed: %s", exc)
        raise

    return {
        "company_name": result.company_name,
        "role_title": result.role_title,
        "hiring_manager": result.hiring_manager,
        "required_skills": result.required_skills,
    }
