"""ChromaDB vector store for CLIP embeddings.

Provides persistent, indexed similarity search for copyright / duplicate
detection, replacing the previous brute-force cosine scan.
"""

from __future__ import annotations

import datetime
from typing import Any

import chromadb

from app.config import settings

_client: chromadb.ClientAPI | None = None
_collection: chromadb.Collection | None = None


def init_chroma() -> chromadb.Collection:
    """Create or open the persistent ChromaDB collection.

    Uses cosine distance (the default) so that query distances map directly
    to `1 - cosine_similarity`.
    """
    global _client, _collection

    if _collection is not None:
        return _collection

    _client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    _collection = _client.get_or_create_collection(
        name=settings.chroma_collection_name,
        metadata={"hnsw:space": "cosine"},
    )
    return _collection


def _get_collection() -> chromadb.Collection:
    if _collection is None:
        return init_chroma()
    return _collection


def add_embedding(
    file_hash: str,
    embedding: list[float],
    *,
    filename: str = "upload",
    uploaded_by: str = "anonymous",
) -> None:
    """Store (or update) an embedding in the vector collection.

    Uses ``file_hash`` as the document ID so the same file is never stored
    twice.
    """
    col = _get_collection()
    col.upsert(
        ids=[file_hash],
        embeddings=[embedding],
        metadatas=[
            {
                "filename": filename,
                "uploaded_by": uploaded_by,
                "created_at": datetime.datetime.utcnow().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            }
        ],
    )


def query_similar(
    embedding: list[float],
    n_results: int = 5,
    threshold: float | None = None,
) -> list[dict[str, Any]]:
    """Return the top-N matches above *threshold*.

    ChromaDB returns cosine *distance* (``1 - similarity``), so we convert
    back to a similarity score for the caller.
    """
    threshold = settings.duplicate_threshold if threshold is None else threshold
    col = _get_collection()

    if col.count() == 0:
        return []

    results = col.query(
        query_embeddings=[embedding],
        n_results=min(n_results, col.count()),
        include=["metadatas", "distances"],
    )

    matches: list[dict[str, Any]] = []
    ids = results["ids"][0]
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]

    for doc_id, dist, meta in zip(ids, distances, metadatas):
        similarity = 1.0 - dist  # cosine distance → cosine similarity
        if similarity >= threshold:
            matches.append(
                {
                    "file_hash": doc_id,
                    "similarity": round(similarity, 4),
                    "filename": meta.get("filename", ""),
                    "uploaded_by": meta.get("uploaded_by", "anonymous"),
                    "uploaded_at": meta.get("created_at", ""),
                }
            )
    return matches
