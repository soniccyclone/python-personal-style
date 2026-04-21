from pathlib import Path

import pytest

from fastapi.testclient import TestClient

from bookmarks.api import create_app
from bookmarks.config import Settings


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    settings = Settings(db_path=tmp_path / 'test.db')
    app = create_app(settings)
    with TestClient(app) as test_client:
        yield test_client


def test_create_then_get_roundtrips(client):
    # Arrange
    payload = {'content': 'hello', 'tags': ['python', 'style']}

    # Act
    create_response = client.post('/notes', json=payload)
    created = create_response.json()
    get_response = client.get(f'/notes/{created["id"]}')

    # Assert
    assert create_response.status_code == 201
    assert created['content'] == 'hello'
    assert created['tags'] == ['python', 'style']
    assert get_response.status_code == 200
    assert get_response.json() == created


def test_list_notes_returns_all(client):
    # Arrange
    client.post('/notes', json={'content': 'one', 'tags': []})
    client.post('/notes', json={'content': 'two', 'tags': []})

    # Act
    response = client.get('/notes')
    notes = response.json()

    # Assert
    assert response.status_code == 200
    assert [n['content'] for n in notes] == ['one', 'two']


def test_list_notes_filters_by_tag(client):
    # Arrange
    client.post('/notes', json={'content': 'pythonic', 'tags': ['python']})
    client.post('/notes', json={'content': 'unrelated', 'tags': ['other']})

    # Act
    response = client.get('/notes', params={'tag': 'python'})
    notes = response.json()

    # Assert
    assert response.status_code == 200
    assert [n['content'] for n in notes] == ['pythonic']


def test_get_missing_note_returns_404(client):
    # Arrange (no notes created)

    # Act
    response = client.get('/notes/9999')

    # Assert
    assert response.status_code == 404
    assert response.json() == {'detail': 'note not found'}


def test_delete_note_removes_it(client):
    # Arrange
    created = client.post('/notes', json={'content': 'to-delete', 'tags': []}).json()

    # Act
    delete_response = client.delete(f'/notes/{created["id"]}')
    followup = client.get(f'/notes/{created["id"]}')

    # Assert
    assert delete_response.status_code == 200
    assert delete_response.json() == created
    assert followup.status_code == 404


def test_delete_missing_note_returns_404(client):
    # Arrange (no notes created)

    # Act
    response = client.delete('/notes/9999')

    # Assert
    assert response.status_code == 404


def test_request_id_header_is_echoed_back(client):
    # Arrange
    inbound_id = 'test-request-42'

    # Act
    response = client.post(
        '/notes',
        json={'content': 'hi', 'tags': []},
        headers={'X-Request-ID': inbound_id},
    )

    # Assert
    assert response.headers['X-Request-ID'] == inbound_id


def test_request_id_is_generated_when_missing(client):
    # Arrange (no X-Request-ID sent)

    # Act
    response = client.post('/notes', json={'content': 'hi', 'tags': []})

    # Assert
    assert 'X-Request-ID' in response.headers
    assert len(response.headers['X-Request-ID']) > 0
