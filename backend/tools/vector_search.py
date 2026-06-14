"""
backend/tools/vector_search.py

FAISS-based vector store for resume section retrieval.

Responsibilities:
  1. embed_and_store_resume() — chunks a resume into ~200-token passages,
     embeds them with all-MiniLM-L6-v2, and persists an on-disk FAISS index
     scoped to the current user + run.
  2. get_retriever()          — loads the persisted FAISS index for a run and
     returns a LangChain retriever ready to be called by the Resume Agent.
  3. retrieve_relevant_sections() — convenience async wrapper that calls the
     retriever and returns plain text passages.

Design notes:
  - One FAISS index is created per run (keyed by run_id) so indexes do not
    bleed across users or applications.
  - Indexes are stored under uploads/faiss_indexes/{run_id}/ so they live
    alongside uploaded files and can be cleaned up together.
  - The embedding model (all-MiniLM-L6-v2) runs locally — no API cost.
  - For production with MongoDB Atlas Search, swap the retriever returned by
    get_retriever() for a MongoDBAtlasVectorSearch retriever without changing
    any agent code (same .invoke() interface).
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

if TYPE_CHECKING:
    from langchain_core.vectorstores import VectorStoreRetriever

logger = logging.getLogger(__name__)

# ─── Constants ─────────────────────────────────────────────────────────────────

EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
CHUNK_SIZE_TOKENS: int = 200          # approximate target chunk size in tokens
CHUNK_OVERLAP_TOKENS: int = 30        # overlap to preserve cross-chunk context
TOP_K_RESULTS: int = 4               # number of passages the retriever returns
FAISS_INDEX_BASE_DIR: str = "uploads/faiss_indexes"

# ─── Shared embedding model (loaded once, reused across calls) ─────────────────
# HuggingFaceEmbeddings caches the model after the first load.

_embeddings: HuggingFaceEmbeddings | None = None


def _get_embeddings() -> HuggingFaceEmbeddings:
    """
    Return the singleton HuggingFaceEmbeddings instance.
    Lazy-loaded on first call to avoid loading the model at import time.
    """
    global _embeddings
    if _embeddings is None:
        logger.info("Loading embedding model: %s", EMBEDDING_MODEL_NAME)
        _embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        logger.info("Embedding model loaded successfully.")
    return _embeddings


# ─── Chunking ──────────────────────────────────────────────────────────────────

def _chunk_resume(resume_text: str) -> list[str]:
    """
    Split resume text into overlapping passages of approximately CHUNK_SIZE_TOKENS.

    Uses a simple word-based splitter (1 word ≈ 1.3 tokens on average) rather
    than a tokenizer to avoid an extra dependency. The slight imprecision is
    acceptable for retrieval — exact token counts are not required.

    Args:
        resume_text: Raw extracted text of the full resume.

    Returns:
        A list of overlapping text chunks ready for embedding.
    """
    words = resume_text.split()
    # Approximate words per chunk: CHUNK_SIZE_TOKENS / 1.3
    words_per_chunk = int(CHUNK_SIZE_TOKENS / 1.3)
    overlap_words = int(CHUNK_OVERLAP_TOKENS / 1.3)

    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = start + words_per_chunk
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += words_per_chunk - overlap_words  # slide with overlap

    logger.debug("Chunked resume into %d passages.", len(chunks))
    return chunks


# ─── Index path helper ─────────────────────────────────────────────────────────

def _index_path(run_id: str) -> Path:
    """Return the directory path where the FAISS index for a run is stored."""
    return Path(FAISS_INDEX_BASE_DIR) / run_id


# ─── Public API ────────────────────────────────────────────────────────────────

def embed_and_store_resume(resume_text: str, run_id: str, user_id: str) -> str:
    """
    Chunk, embed, and persist a FAISS index for the given resume.

    This should be called immediately after the resume is parsed (in the upload
    route or just before the graph is invoked) so the index is ready when the
    Resume Agent needs it.

    Args:
        resume_text: Full raw text of the candidate's resume.
        run_id: UUID of the current co-pilot run (used to name the index directory).
        user_id: Authenticated user's UUID (stored in Document metadata for auditability).

    Returns:
        The absolute path to the saved FAISS index directory as a string.

    Raises:
        ValueError: If resume_text is empty.
        OSError: If the index directory cannot be created or written.
    """
    if not resume_text.strip():
        raise ValueError("resume_text is empty — cannot build FAISS index.")

    chunks = _chunk_resume(resume_text)

    # Wrap chunks in LangChain Document objects with metadata
    documents = [
        Document(
            page_content=chunk,
            metadata={
                "run_id": run_id,
                "user_id": user_id,
                "chunk_index": idx,
            },
        )
        for idx, chunk in enumerate(chunks)
    ]

    embeddings = _get_embeddings()
    index_dir = _index_path(run_id)
    index_dir.mkdir(parents=True, exist_ok=True)

    logger.info(
        "Building FAISS index for run_id=%s with %d chunks...", run_id, len(documents)
    )
    vectorstore = FAISS.from_documents(documents, embeddings)
    vectorstore.save_local(str(index_dir))
    logger.info("FAISS index saved to %s", index_dir)

    return str(index_dir.resolve())


def get_retriever(run_id: str) -> "VectorStoreRetriever":
    """
    Load the persisted FAISS index for a run and return a retriever.

    The retriever is compatible with any LangChain retrieval chain —
    call retriever.invoke(query) or retriever.ainvoke(query) to get
    the top-K most relevant Document objects.

    Args:
        run_id: UUID of the co-pilot run whose index to load.

    Returns:
        A VectorStoreRetriever configured for top-K semantic search.

    Raises:
        FileNotFoundError: If no index exists for the given run_id.
        RuntimeError: If the FAISS index fails to load.
    """
    index_dir = _index_path(run_id)
    if not index_dir.exists():
        raise FileNotFoundError(
            f"No FAISS index found for run_id='{run_id}'. "
            f"Expected directory: {index_dir}. "
            "Ensure embed_and_store_resume() was called before invoking the graph."
        )

    embeddings = _get_embeddings()
    logger.info("Loading FAISS index from %s", index_dir)

    try:
        vectorstore = FAISS.load_local(
            str(index_dir),
            embeddings,
            allow_dangerous_deserialization=True,  # safe: we wrote this index ourselves
        )
    except Exception as exc:
        raise RuntimeError(f"Failed to load FAISS index for run_id='{run_id}': {exc}") from exc

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": TOP_K_RESULTS},
    )
    logger.info("FAISS retriever ready for run_id=%s (top_k=%d)", run_id, TOP_K_RESULTS)
    return retriever


async def retrieve_relevant_sections(query: str, run_id: str) -> str:
    """
    Retrieve the most relevant resume passages for a given query.

    This is the primary entry point for the Resume Agent. It loads the
    FAISS index, runs a semantic similarity search, and returns the
    matching passages as a single concatenated string.

    Args:
        query: The search query — typically a key skill or job requirement
               from the JD (e.g., "Python backend experience with FastAPI").
        run_id: UUID of the co-pilot run whose resume index to search.

    Returns:
        A newline-separated string of the top-K most relevant resume passages.
        Returns an empty string if no index exists (graceful degradation).

    Raises:
        RuntimeError: If the FAISS retrieval itself fails unexpectedly.
    """
    try:
        retriever = get_retriever(run_id)
    except FileNotFoundError:
        logger.warning(
            "No FAISS index for run_id=%s — returning empty sections. "
            "The Resume Agent will proceed without vector retrieval.",
            run_id,
        )
        return ""

    try:
        docs = await retriever.ainvoke(query)
        passages = "\n\n---\n\n".join(doc.page_content for doc in docs)
        logger.info(
            "Retrieved %d passages for query '%s' (run_id=%s)",
            len(docs),
            query,
            run_id,
        )
        return passages
    except Exception as exc:
        raise RuntimeError(
            f"FAISS retrieval failed for query='{query}', run_id='{run_id}': {exc}"
        ) from exc
