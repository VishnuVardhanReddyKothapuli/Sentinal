"""Exercise the real local Qdrant storage without downloading vision weights."""
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

pytest.importorskip('qdrant_client')
from ai_engine import vectors


def test_local_persistence_tenant_scope_and_concurrent_access(tmp_path, monkeypatch):
    monkeypatch.setenv('QDRANT_URL', '')
    monkeypatch.setenv('QDRANT_LOCAL_PATH', str(tmp_path / 'vectors'))
    vector = [1.0] + [0.0] * 511
    matches, _ = vectors.search_and_store(vector, 'alice', 'first')
    assert matches == []
    matches, _ = vectors.search_and_store(vector, 'bob', 'foreign')
    assert matches == []
    # Each operation closes/reopens storage, proving disk persistence too.
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(lambda i: vectors.search_and_store(vector, 'alice', f'copy-{i}'), range(3)))
    for matches, _ in results:
        assert any(match['record_id'] == 'first' and match['score'] > 99 for match in matches)
        assert all(match['record_id'] != 'foreign' for match in matches)
    vectors.delete('first', 'bob')
    matches, _ = vectors.search_and_store(vector, 'alice', 'still-present')
    assert any(match['record_id'] == 'first' for match in matches)
    vectors.delete('first', 'alice')
    matches, _ = vectors.search_and_store(vector, 'alice', 'after-delete')
    assert all(match['record_id'] != 'first' for match in matches)


def test_remote_filter_indexes_are_created_before_search(monkeypatch):
    monkeypatch.setenv('QDRANT_URL', 'https://test-cluster.example.com')
    client = MagicMock()
    client.collection_exists.return_value = True
    client.get_collection.return_value = SimpleNamespace(payload_schema={'user_id': object()})
    client.query_points.return_value = SimpleNamespace(points=[])
    monkeypatch.setattr(vectors, '_client', lambda: client)
    vectors.search_and_store([1.0] + [0.0] * 511, 'alice', 'first')
    assert client.create_payload_index.call_count == 1
    assert client.create_payload_index.call_args.kwargs['field_name'] == 'record_id'
    names = [call[0] for call in client.mock_calls]
    assert names.index('create_payload_index') < names.index('query_points')
    client.close.assert_called_once()
