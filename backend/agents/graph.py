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

from backend.agents.cover_letter import cover_letter_agent
from backend.agents.hitl import hitl_node
from backend.agents.interview_prep import interview_prep_agent
from backend.agents.outreach import outreach_agent
from backend.agents.research import research_agent
from backend.agents.resume import resume_agent
from backend.agents.state import ApplicationState
from backend.agents.supervisor import supervisor_agent
from backend.agents.tracker import tracker_node
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

    # Resume: async node (FAISS retrieval + LLM rewrite)
    builder.add_node(
        "resume",
        resume_agent,
        retry=RetryPolicy(max_attempts=3),
    )

    # Cover Letter: async node
    builder.add_node("cover_letter", cover_letter_agent, retry=RetryPolicy(max_attempts=3))

    # Interview Prep: async node
    builder.add_node("interview_prep", interview_prep_agent, retry=RetryPolicy(max_attempts=3))

    # Outreach: async node
    builder.add_node("outreach", outreach_agent, retry=RetryPolicy(max_attempts=3))

    # HITL: pass-through
    builder.add_node("hitl_checkpoint", hitl_node)

    # Tracker: final save
    builder.add_node("tracker", tracker_node)

    # ── Edges ──────────────────────────────────────────────────────────────────
    builder.add_edge(START, "supervisor")
    builder.add_edge("supervisor", "research")
    builder.add_edge("supervisor", "resume")
    
    # Phase 2 — Fan out: After BOTH Phase 1 agents complete
    builder.add_edge("research", "cover_letter")
    builder.add_edge("resume", "cover_letter")
    
    builder.add_edge("research", "interview_prep")
    builder.add_edge("resume", "interview_prep")
    
    builder.add_edge("research", "outreach")
    builder.add_edge("resume", "outreach")

    # Fan-in: All Phase 2 agents -> HITL checkpoint
    builder.add_edge("cover_letter", "hitl_checkpoint")
    builder.add_edge("interview_prep", "hitl_checkpoint")
    builder.add_edge("outreach", "hitl_checkpoint")

    # HITL -> Tracker -> END
    builder.add_edge("hitl_checkpoint", "tracker")
    builder.add_edge("tracker", END)

    # ── Compile with checkpointer ──────────────────────────────────────────────
    checkpointer = get_checkpointer()
    compiled = builder.compile(checkpointer=checkpointer)

    logger.info("LangGraph compiled: supervisor → research (minimal phase-1 graph)")
    return compiled


# ─── Singleton graph instance ─────────────────────────────────────────────────
# Compiled once at import time and reused for every request.
# The checkpointer isolates state per thread_id (= run_id).

graph = _build_graph()
