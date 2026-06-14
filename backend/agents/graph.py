"""
backend/agents/graph.py

LangGraph DAG — current phase: Supervisor + Research (minimal testable graph).

Graph topology (Phase 1 only):

    START → supervisor → research → END

This will be expanded to the full two-phase parallel DAG as more agents are built:

    START → supervisor ─┬→ research ──┬→ cover_letter   ─┐
                        └→ resume   ──┤→ interview_prep ─┤→ hitl → tracker → END
                                      └→ outreach       ─┘

All LLM nodes carry RetryPolicy(max_attempts=3) as required by architecture rules.
The graph is compiled once at module load time and reused across all requests.
"""

from __future__ import annotations

import logging

from langgraph.graph import END, START, StateGraph
from langgraph.types import RetryPolicy

from backend.agents.research import research_agent
from backend.agents.state import ApplicationState
from backend.agents.supervisor import supervisor_agent
from backend.memory.checkpointer import get_checkpointer

logger = logging.getLogger(__name__)

# ─── Build the graph ──────────────────────────────────────────────────────────

def _build_graph():
    """
    Construct and compile the LangGraph StateGraph.

    Returns:
        A compiled LangGraph graph with MongoDB checkpointer attached.
    """
    builder = StateGraph(ApplicationState)

    # ── Nodes ──────────────────────────────────────────────────────────────────
    # Supervisor: sync node (structured output, fast)
    builder.add_node(
        "supervisor",
        supervisor_agent,
        retry=RetryPolicy(max_attempts=3),
    )

    # Research: async node (Tavily + LLM synthesis)
    builder.add_node(
        "research",
        research_agent,
        retry=RetryPolicy(max_attempts=3),
    )

    # ── Edges ──────────────────────────────────────────────────────────────────
    builder.add_edge(START, "supervisor")
    builder.add_edge("supervisor", "research")
    builder.add_edge("research", END)

    # ── Compile with checkpointer ──────────────────────────────────────────────
    checkpointer = get_checkpointer()
    compiled = builder.compile(checkpointer=checkpointer)

    logger.info("LangGraph compiled: supervisor → research (minimal phase-1 graph)")
    return compiled


# ─── Singleton graph instance ─────────────────────────────────────────────────
# Compiled once at import time and reused for every request.
# The checkpointer isolates state per thread_id (= run_id).

graph = _build_graph()
