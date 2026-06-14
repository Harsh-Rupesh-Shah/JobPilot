"""
backend/tools/search.py

Tavily web search tool for the Research Agent.

Wraps TavilySearchResults as a LangChain @tool so it can be bound to the
Research Agent via llm.bind_tools(). Also exposes a plain async helper
`run_web_search()` for use in agent nodes that invoke the tool directly
rather than via tool-calling.
"""

from __future__ import annotations

import logging
from typing import Any

import os

from langchain_core.tools import tool
from langchain_tavily import TavilySearch

from backend.core.config import settings

logger = logging.getLogger(__name__)

# ─── Tavily client ─────────────────────────────────────────────────────────────
# max_results=5 is the sweet spot: enough context without blowing the context window.
# include_raw_content=False keeps output clean (summaries only, no raw HTML dumps).
# include_answer=True lets Tavily return a direct answer when available.
# TavilySearch reads TAVILY_API_KEY from the environment automatically via its
# internal TavilySearchAPIWrapper — we set it from settings before instantiating.

os.environ.setdefault("TAVILY_API_KEY", settings.TAVILY_API_KEY)

_tavily_client = TavilySearch(
    max_results=5,
    include_answer=True,
    include_raw_content=False,
)


# ─── LangChain @tool decorator ─────────────────────────────────────────────────
# This decorated function is what gets bound to the Research Agent via
# llm.bind_tools([web_search_tool]). LangChain uses the docstring as the
# tool description sent to the LLM so it knows when and how to call it.

import asyncio

@tool
async def web_search_tool(query: str) -> list[dict[str, Any]]:
    """
    Search the web for up-to-date information about a company, role, or person.

    Use this tool to research:
    - Company overview, products, business model, and stage
    - Engineering culture, tech stack, and open-source activity
    - Recent news: funding rounds, product launches, acquisitions (last 12 months)
    - Role-specific context and success metrics
    - Hiring manager public profile or written content

    Args:
        query: A specific, targeted search query string. Be as precise as possible.
               Examples:
               - "Stripe engineering blog tech stack 2024"
               - "OpenAI recent funding round news 2025"
               - "Senior ML Engineer role responsibilities tech startup"

    Returns:
        A list of search result dicts, each with keys:
        - 'url': source URL
        - 'content': page summary
        - 'score': Tavily relevance score (higher is more relevant)
    """
    logger.info("Web search query: %s", query)
    
    # Simple retry logic for intermittent API failures
    for attempt in range(3):
        try:
            results: list[dict[str, Any]] = await _tavily_client.ainvoke(query)
            logger.info("Web search returned %d results for query: %s", len(results), query)
            return results
        except Exception as exc:
            if attempt < 2:
                logger.warning("Web search failed for query '%s' (attempt %d). Retrying... Error: %s", query, attempt + 1, exc)
                await asyncio.sleep(1)
            else:
                logger.error("Web search failed for query '%s' after 3 attempts: %s", query, exc)
                raise


# ─── Plain async helper (for direct agent node use) ────────────────────────────

async def run_web_search(query: str) -> list[dict[str, Any]]:
    """
    Async convenience wrapper around the Tavily client for use in async agent nodes.

    Call this directly in agent node functions instead of going through the
    @tool decorator when you do not need LangChain tool-calling mechanics.

    Args:
        query: A specific, targeted search query string.

    Returns:
        A list of search result dicts from Tavily.

    Raises:
        RuntimeError: If the Tavily API call fails after exhausting retries.
    """
    logger.info("Async web search query: %s", query)
    try:
        results: list[dict[str, Any]] = await _tavily_client.ainvoke(query)
        logger.info("Async web search returned %d results", len(results))
        return results
    except Exception as exc:
        logger.error("Async web search failed for query '%s': %s", query, exc)
        raise RuntimeError(f"Web search failed: {exc}") from exc
