"""
backend/llm/model.py

Centralised LLM factory for the AI Job Co-Pilot.

All agents import their LLM instances from here — never construct ChatOpenRouter
directly inside an agent file. This means:

  - Model names are configured in config.py (env-overridable via .env).
  - Switching providers or models requires changing one file, not every agent.
  - Temperature and token budgets are documented in one place.

Exported objects
----------------
llm_writer       : ChatOpenRouter — DeepSeek R1 (reasoning, writing, synthesis)
llm_coder        : ChatOpenRouter — Qwen3-Coder (structured resume rewriting)
get_structured_llm(schema) : returns llm_writer bound to a Pydantic schema via
                             .with_structured_output() — used by the Supervisor Agent.

Usage in an agent
-----------------
    from backend.llm.model import llm_writer, llm_coder, get_structured_llm
    from mymodule import MyOutputSchema

    # Plain streaming LLM
    response = await llm_writer.ainvoke(messages)

    # Structured output (no streaming — returns Pydantic model directly)
    structured = get_structured_llm(MyOutputSchema)
    result: MyOutputSchema = structured.invoke(prompt)
"""

from __future__ import annotations

import logging
from typing import Type

from langchain_core.language_models import BaseChatModel
from langchain_openrouter import ChatOpenRouter
from pydantic import BaseModel

from backend.core.config import settings

logger = logging.getLogger(__name__)


# ─── Writer LLM — reasoning, writing, synthesis ───────────────────────────────
# Used by: Supervisor, Research, Cover Letter, Interview Prep, Outreach agents.
# Model: DeepSeek R1 0528 (free tier via OpenRouter)
# Temperature 0.3 — enough creativity for writing; not deterministic like extraction.

llm_writer: ChatOpenRouter = ChatOpenRouter(
    model=settings.LLM_WRITER_MODEL,
    openrouter_api_key=settings.OPENROUTER_API_KEY,
    temperature=0.3,
    max_tokens=2048,
    streaming=True,
)


# ─── Coder LLM — structured resume rewriting ──────────────────────────────────
# Used by: Resume Agent only.
# Model: Qwen3-Coder (free tier via OpenRouter)
# Temperature 0.1 — near-deterministic; resume rewriting needs precision.

llm_coder: ChatOpenRouter = ChatOpenRouter(
    model=settings.LLM_CODER_MODEL,
    openrouter_api_key=settings.OPENROUTER_API_KEY,
    temperature=0.1,
    max_tokens=3000,   # resume rewrites can be long
    streaming=True,
)


# ─── Structured output factory ────────────────────────────────────────────────

def get_structured_llm(schema: Type[BaseModel]) -> BaseChatModel:
    """
    Return a version of llm_writer bound to a Pydantic output schema.

    Uses .with_structured_output() to force the LLM to return a validated
    Pydantic model instance instead of raw text. Streaming is automatically
    disabled for structured output (LangChain requirement).

    Args:
        schema: A Pydantic BaseModel subclass defining the expected output shape.

    Returns:
        A runnable that accepts a prompt string and returns an instance of `schema`.

    Example:
        structured = get_structured_llm(SupervisorOutput)
        result: SupervisorOutput = structured.invoke(prompt)
    """
    # Structured output uses a non-streaming variant (temperature 0 for extraction)
    base_llm = ChatOpenRouter(
        model=settings.LLM_WRITER_MODEL,
        openrouter_api_key=settings.OPENROUTER_API_KEY,
        temperature=0,      # deterministic — structured extraction requires consistency
        max_tokens=512,     # metadata extraction is compact
        streaming=False,    # streaming is incompatible with structured output parsing
    )
    logger.debug("Building structured LLM for schema: %s", schema.__name__)
    return base_llm.with_structured_output(schema)
