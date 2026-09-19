"""Qdrant cosine search with mandatory tenant constraints on reads and deletes."""

import os
import threading
import uuid
from contextlib import contextmanager

_COLLECTION_LOCK = threading.Lock()
COLLECTION = "sentinel_embeddings"


def _client():
    from qdrant_client import QdrantClient
    url = os.getenv("QDRANT_URL")
    if url:
        return QdrantClient(url=url, api_key=os.getenv("QDRANT_API_KEY") or None, timeout=15)
    local_path = os.getenv("QDRANT_LOCAL_PATH")
    if local_path:
        return QdrantClient(path=local_path)
    raise RuntimeError("Configure QDRANT_URL or QDRANT_LOCAL_PATH")


@contextmanager
def _connection():
    # Local Qdrant permits one open client per storage directory. Serialize the
    # full operation, including close, across analysis and deletion threads.
    with _COLLECTION_LOCK:
        client = _client()
        try:
            yield client
        finally:
            client.close()


def tenant_filter(user_id: str, record_id: str | None = None):
    from qdrant_client import models
    if not user_id:
        raise ValueError("Tenant identity is required")
    conditions = [models.FieldCondition(key="user_id", match=models.MatchValue(value=user_id))]
    if record_id:
        conditions.append(models.FieldCondition(key="record_id", match=models.MatchValue(value=record_id)))
    return models.Filter(must=conditions)


def _ensure_filter_indexes(client):
    # Cloud strict mode rejects unindexed tenant/record filters. Local mode
    # evaluates filters directly and does not implement payload indexes.
    if not os.getenv("QDRANT_URL"):
        return
    from qdrant_client import models
    schema = client.get_collection(COLLECTION).payload_schema or {}
    for field in ("user_id", "record_id"):
        if field not in schema:
            client.create_payload_index(collection_name=COLLECTION, field_name=field,
                                        field_schema=models.PayloadSchemaType.KEYWORD, wait=True)


def search_and_store(vector: list[float], user_id: str, record_id: str) -> tuple[list[dict], str]:
    from qdrant_client import models
    query_filter = tenant_filter(user_id)
    with _connection() as client:
        if not client.collection_exists(COLLECTION):
            client.create_collection(COLLECTION, vectors_config=models.VectorParams(size=512, distance=models.Distance.COSINE))
        _ensure_filter_indexes(client)
        query_filter.must_not = [models.FieldCondition(key="record_id", match=models.MatchValue(value=record_id))]
        result = client.query_points(collection_name=COLLECTION, query=vector, query_filter=query_filter, limit=5, score_threshold=0.70, with_payload=True)
        matches = []
        for point in result.points:
            payload = point.payload or {}
            # Defense in depth: never surface cross-account payloads even from a misconfigured service.
            if payload.get("user_id") == user_id and payload.get("record_id") != record_id:
                matches.append({"record_id": payload["record_id"], "score": round(max(0, min(100, point.score * 100)), 2), "cosine_score": float(point.score)})
        vector_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"sentinel:{user_id}:{record_id}"))
        client.upsert(collection_name=COLLECTION, points=[models.PointStruct(id=vector_id, vector=vector, payload={"user_id": user_id, "record_id": record_id})], wait=True)
        return sorted(matches, key=lambda match: match["score"], reverse=True), vector_id


def delete(record_id: str, user_id: str) -> None:
    from qdrant_client import models
    constraint = tenant_filter(user_id, record_id)
    with _connection() as client:
        if client.collection_exists(COLLECTION):
            _ensure_filter_indexes(client)
            client.delete(collection_name=COLLECTION, points_selector=models.FilterSelector(filter=constraint), wait=True)
