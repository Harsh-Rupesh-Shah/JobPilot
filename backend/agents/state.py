"""
backend/agents/state.py

Defines ApplicationState — the single shared TypedDict that flows through every
node in the LangGraph DAG. Every agent reads from and writes to this state.
"""

from __future__ import annotations

from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class ApplicationState(TypedDict):
    """
    Shared state for the AI Job Co-Pilot LangGraph DAG.

    Inputs are set once at graph invocation time.
    Intermediate outputs are populated by agents during execution.
    Control-flow fields are managed automatically by LangGraph.
    Metadata fields are set by the FastAPI layer before invoking the graph.
    """

    # ─── Inputs (set by FastAPI before graph.invoke) ───────────────────────────
    resume_text: str
    """Raw text extracted from the uploaded PDF or DOCX resume."""

    job_description: str
    """Full job description text — either scraped from a URL or pasted manually."""

    job_url: str
    """Source URL of the job posting (empty string if user pasted JD directly)."""

    # ─── Supervisor-extracted metadata (populated in Phase 0) ──────────────────
    company_name: str
    """Company name extracted from the job description by the Supervisor Agent."""

    role_title: str
    """Job title / role extracted from the job description by the Supervisor Agent."""

    hiring_manager: str
    """Hiring manager name if found in the JD; empty string otherwise."""

    required_skills: list[str]
    """List of key required skills extracted from the JD by the Supervisor Agent."""

    # ─── Phase 1 outputs (populated in parallel by Research + Resume agents) ───
    research_brief: str
    """Company & role research summary produced by the Research Agent."""

    tailored_resume: str
    """ATS-optimised, tailored resume produced by the Resume Agent."""

    # ─── Phase 2 outputs (populated in parallel by 3 agents) ──────────────────
    cover_letter: str
    """Personalised cover letter produced by the Cover Letter Agent."""

    interview_qa: str
    """Role-specific interview Q&A in STAR format, produced by the Interview Prep Agent."""

    outreach_draft: str
    """Cold outreach email draft produced by the Outreach Agent (never sent automatically)."""

    # ─── Control flow (managed by LangGraph message reducer) ──────────────────
    messages: Annotated[list, add_messages]
    """Accumulated chat / agent messages within a single run. Managed by add_messages."""

    # ─── Metadata (set by FastAPI before graph.invoke) ─────────────────────────
    run_id: str
    """UUID for this co-pilot run — used as the LangGraph thread_id."""

    user_id: str
    """Authenticated user's UUID — scopes checkpointer threads and long-term memory."""

    timestamp: str
    """ISO-8601 UTC timestamp of when this run was initiated."""
