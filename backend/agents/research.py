"""
backend/agents/research.py

Research Agent — Phase 1 of the LangGraph DAG (runs in parallel with Resume Agent).

Uses Tavily web search to compile a structured research brief about the target
company and role. The brief is consumed by the Cover Letter, Interview Prep,
and Outreach agents in Phase 2.

Strategy: issue 3 targeted search queries in sequence, then synthesise all
results into the structured brief format defined in the research prompt.
"""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from backend.agents.state import ApplicationState
from backend.llm.model import llm_writer
from backend.prompts.research import RESEARCH_SYSTEM_PROMPT
from backend.tools.search import run_web_search

logger = logging.getLogger(__name__)


# ─── Result formatter ─────────────────────────────────────────────────────────

def _format_search_results(results: list[dict[str, Any]]) -> str:
    """
    Format a list of Tavily search result dicts into a readable string
    for injection into the LLM prompt.

    Args:
        results: List of dicts with keys 'url', 'content', 'score'.

    Returns:
        A formatted multi-line string summarising all search results.
    """
    if not results:
        return "No search results found."

    lines: list[str] = []
    for i, r in enumerate(results, start=1):
        url = r.get("url", "unknown")
        content = r.get("content", "").strip()
        lines.append(f"[Result {i}] {url}\n{content}\n")

    return "\n".join(lines)


# ─── Agent node ───────────────────────────────────────────────────────────────

async def research_agent(state: ApplicationState, config: RunnableConfig) -> dict[str, Any]:
    """
    LangGraph node: research the target company and role using web search.

    Strategy:
      1. Issue 3 targeted Tavily queries for: company overview, tech/engineering
         culture, and recent news.
      2. Concatenate all search results.
      3. Pass results + JD to DeepSeek for synthesis into the structured brief.

    Reads:
        state["company_name"]      — set by Supervisor
        state["role_title"]        — set by Supervisor
        state["hiring_manager"]    — set by Supervisor (may be empty)
        state["job_description"]   — raw JD text

    Writes to state:
        research_brief             — structured markdown research brief

    Returns:
        A dict with only the keys this agent is responsible for updating.
    """
    run_id = state.get("run_id", "unknown")
    company = state.get("company_name", "")
    role = state.get("role_title", "")
    hiring_manager = state.get("hiring_manager", "")
    job_description = state.get("job_description", "")

    logger.info("Research agent starting: company=%s, role=%s, run_id=%s", company, role, run_id)

    if not company:
        logger.warning("Research agent: company_name is empty, using generic queries.")

    # ── Step 1: Issue targeted search queries ──────────────────────────────────
    queries = [
        f"{company} company overview products business model",
        f"{company} engineering culture tech stack developer blog",
        f"{company} {role} recent news 2025",
    ]

    all_results: list[str] = []
    for query in queries:
        logger.info("Tavily query: %s", query)
        try:
            results = await run_web_search(query)
            formatted = _format_search_results(results)
            all_results.append(f"=== Query: {query} ===\n{formatted}")
        except Exception as exc:
            logger.warning("Search query failed ('%s'): %s — continuing.", query, exc)
            all_results.append(f"=== Query: {query} ===\nSearch failed: {exc}\n")

    combined_results = "\n\n".join(all_results)

    # ── Step 2: Synthesise with LLM ────────────────────────────────────────────
    system_prompt = RESEARCH_SYSTEM_PROMPT.format(
        company_name=company,
        role_title=role,
        hiring_manager=hiring_manager,
        job_description=job_description,
    )

    synthesis_prompt = (
        f"Here are the web search results I gathered:\n\n"
        f"{combined_results}\n\n"
        f"Now synthesise these into the structured research brief format defined in your instructions."
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=synthesis_prompt),
    ]

    try:
        response = await llm_writer.ainvoke(messages, config)
        research_brief: str = response.content
        logger.info(
            "Research agent complete: brief length=%d chars, run_id=%s",
            len(research_brief),
            run_id,
        )
    except Exception as exc:
        logger.error("Research agent LLM synthesis failed: %s", exc)
        raise

    return {"research_brief": research_brief}
