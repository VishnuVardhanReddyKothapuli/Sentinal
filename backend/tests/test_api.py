"""API integration tests use explicit mock inference; they never claim model accuracy."""
from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.config import Settings
from app.main import create_app
from app.models import User


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr('app.main.capabilities', lambda: {'nsfw': False, 'similarity': False})

    async def fake_analysis(path, mode, user_id, record_id):
        return {'overall_status': 'REVIEW', 'scores': None, 'warnings': ['Mock inference for API integration testing'], 'matches': [], 'capabilities': {'nsfw': False}, 'checks_complete': {'similarity': False}}

    async def fake_delete(record_id, user_id):
        return None

    monkeypatch.setattr('app.main.run_analysis', fake_analysis)
    monkeypatch.setattr('app.main.remove_vector', fake_delete)
    application = create_app(Settings(database_url=f'sqlite:///{tmp_path / "test.db"}', data_dir=tmp_path, upload_dir=tmp_path / 'uploads', jwt_secret='testing-only-secret-with-at-least-32-characters', max_upload_mb=1))
    with TestClient(application) as test_client:
        yield test_client


def register(client, name='alice'):
    response = client.post('/api/v1/auth/register', json={'username': name, 'email': f'{name}@example.com', 'password': 'test-password-strong'})
    assert response.status_code == 201, response.text
    data = response.json()
    return {'Authorization': f'Bearer {data["access_token"]}'}, data['user']


def image_bytes():
    output = BytesIO()
    Image.new('RGB', (24, 24), '#00aabb').save(output, format='PNG')
    return output.getvalue()


def upload(client, auth, name='example.png', content=None, mode='combined'):
    return client.post(f'/api/v1/analyze/{mode}', headers=auth, files={'file': (name, content if content is not None else image_bytes(), 'image/png')})


def test_registration_login_and_role_injection(client):
    auth, user = register(client)
    assert user['role'] == 'USER'
    assert 'hashed_password' not in user
    assert client.get('/api/v1/auth/me', headers=auth).json()['username'] == 'alice'
    assert client.post('/api/v1/auth/login', json={'username': 'ALICE', 'password': 'test-password-strong'}).status_code == 200
    assert client.post('/api/v1/auth/login', json={'username': 'alice', 'password': 'wrong'}).status_code == 401
    assert client.post('/api/v1/auth/register', json={'username': 'alice', 'email': 'alice@example.com', 'password': 'test-password-strong'}).status_code == 409
    assert client.post('/api/v1/auth/register', json={'username': 'admin', 'email': 'admin@example.com', 'password': 'test-password-strong', 'role': 'ADMIN'}).status_code == 422


def test_authentication_and_admin_guards(client):
    auth, _ = register(client)
    assert client.get('/api/v1/user/history').status_code == 401
    assert client.get('/api/v1/user/history', headers={'Authorization': 'Bearer invalid'}).status_code == 401
    assert client.get('/api/v1/admin/overview', headers=auth).status_code == 403
    assert client.post('/api/v1/admin/purge', headers=auth, json={'ids': ['missing']}).status_code == 403


def test_upload_persistence_account_isolation_and_private_media(client):
    alice, _ = register(client)
    bob, _ = register(client, 'bob')
    response = upload(client, alice)
    assert response.status_code == 201, response.text
    record = response.json()
    assert record['overall_status'] == 'REVIEW'
    assert record['scores'] is None
    assert record['analysis_type'] == 'COMBINED'
    assert record['file_type'] == 'IMAGE'
    history = client.get('/api/v1/user/history', headers=alice).json()
    assert history['total'] == 1
    assert client.get('/api/v1/user/history', headers=bob).json()['items'] == []
    assert client.get(f'/api/v1/user/history/{record["id"]}', headers=bob).status_code == 404
    assert client.delete(f'/api/v1/user/history/{record["id"]}', headers=bob).status_code == 404
    assert client.get(record['file_url']).status_code == 401
    assert client.get(record['file_url'], headers=bob).status_code == 404
    assert client.get(record['file_url'], headers=alice).content == image_bytes()
    assert client.get('/api/v1/metrics/public').json() == {'total_scans': 1, 'flagged_count': 0, 'registered_users': 2}


@pytest.mark.parametrize(('name', 'content', 'code'), [('fake.png', b'<script>danger</script>', 422), ('file.exe', b'MZ', 415), ('empty.png', b'', 422), ('wrong.jpg', None, 422), ('bad.mp4', b'broken video', 422), ('large.png', b'x' * (1024 * 1024 + 1), 413)], ids=['fake-image', 'unsupported-type', 'empty', 'mismatched-extension', 'broken-video', 'over-limit'])
def test_invalid_uploads_are_rejected_and_cleaned(client, name, content, code):
    auth, _ = register(client)
    response = upload(client, auth, name, content)
    assert response.status_code == code, response.text
    assert list(client.app.state.settings.upload_dir.iterdir()) == []
    assert client.get('/api/v1/user/history', headers=auth).json()['total'] == 0


def test_failure_rolls_back_and_cleans_media(client, monkeypatch):
    auth, _ = register(client)

    async def failure(*args):
        raise RuntimeError('private implementation detail')

    monkeypatch.setattr('app.main.run_analysis', failure)
    response = upload(client, auth)
    assert response.status_code == 503
    assert 'private implementation detail' not in response.text
    assert list(client.app.state.settings.upload_dir.iterdir()) == []
    assert client.get('/api/v1/metrics/public').json()['total_scans'] == 0


def test_history_filter_pagination_and_delete_without_vector_service(client, monkeypatch):
    auth, _ = register(client)
    first = upload(client, auth, 'one.png').json()
    upload(client, auth, 'two.png')
    assert client.get('/api/v1/user/history?page_size=1&page=2', headers=auth).json()['items'][0]['id'] == first['id']
    assert client.get('/api/v1/user/history?search=two&status=REVIEW', headers=auth).json()['total'] == 1
    assert client.get('/api/v1/user/history?status=SAFE', headers=auth).json()['total'] == 0

    async def unavailable(*args):
        raise RuntimeError('Vector service should not be called without a vector id')

    monkeypatch.setattr('app.main.remove_vector', unavailable)
    assert client.delete(f'/api/v1/user/history/{first["id"]}', headers=auth).json() == {'deleted': 1}
    assert client.get(first['file_url'], headers=auth).status_code == 404
    assert client.get('/api/v1/metrics/public').json()['total_scans'] == 1


def test_admin_overview_and_bulk_delete(client):
    auth, _ = register(client)
    admin_auth, admin = register(client, 'operator')
    with client.app.state.session_factory() as session:
        session.get(User, admin['id']).role = 'ADMIN'
        session.commit()
    ids = [upload(client, auth).json()['id'] for _ in range(2)]
    overview = client.get('/api/v1/admin/overview', headers=admin_auth)
    assert overview.status_code == 200
    assert overview.json()['total_scans'] == 2
    assert len(overview.json()['logs']) >= 4
    assert client.post('/api/v1/admin/purge', headers=admin_auth, json={'ids': ids}).json() == {'deleted': 2}
    assert client.get('/api/v1/metrics/public').json()['total_scans'] == 0
    assert list(client.app.state.settings.upload_dir.iterdir()) == []


def test_real_video_decode_with_mock_inference(client, tmp_path):
    import cv2
    import numpy as np
    source = tmp_path / 'fixture.avi'
    writer = cv2.VideoWriter(str(source), cv2.VideoWriter_fourcc(*'MJPG'), 5, (32, 32))
    assert writer.isOpened()
    for _ in range(10):
        writer.write(np.zeros((32, 32, 3), dtype=np.uint8))
    writer.release()
    auth, _ = register(client)
    response = upload(client, auth, 'fixture.avi', source.read_bytes())
    assert response.status_code == 201, response.text
    assert response.json()['file_type'] == 'VIDEO'


def test_health_reports_actual_capabilities(client):
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    assert response.json()['capabilities']['nsfw'] is False


def test_foreign_similarity_matches_are_filtered(client, monkeypatch):
    alice, _ = register(client)
    bob, _ = register(client, 'bob')
    foreign_id = upload(client, bob).json()['id']
    own_id = upload(client, alice).json()['id']

    async def matching(*args):
        return {'overall_status': 'REVIEW', 'matches': [{'record_id': foreign_id, 'score': 99}, {'record_id': own_id, 'score': 73}], 'similarity_score': 99, 'is_duplicate': True, 'checks_complete': {'similarity': True}}

    monkeypatch.setattr('app.main.run_analysis', matching)
    response = upload(client, alice, mode='similarity')
    assert response.status_code == 201, response.text
    result = response.json()
    assert len(result['matches']) == 1
    assert result['matches'][0]['record_id'] == own_id
    assert result['similarity_score'] == 73
    assert result['is_duplicate'] is False
    assert result['warnings']


def test_completed_similarity_without_matches_reports_zero(client, monkeypatch):
    auth, _ = register(client)

    async def no_match(*args):
        return {'overall_status': 'SAFE', 'matches': [], 'similarity_score': 0, 'checks_complete': {'similarity': True}}

    monkeypatch.setattr('app.main.run_analysis', no_match)
    result = upload(client, auth, mode='similarity').json()
    assert result['similarity_score'] == 0
    assert result['is_duplicate'] is False
