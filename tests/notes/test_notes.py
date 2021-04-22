import json
import pytest
from starlette.testclient import TestClient

from app.internal.notes import notes


def test_create_note(notes_test_client: TestClient, monkeypatch):
    dummy_user = {
        "username": "new_user",
        "email": "my@email.po",
        "full_name": "My Name",
        "language_id": 1,
        "description": "Happy new user!",
        "target_weight": None,
        "id": 1,
        "is_active": False,
    }
    test_request_payload = {
        "title": "something",
        "description": "something else",
    }
    test_response_payload = {
        "id": 1,
        "title": "something",
        "description": "something else",
        "timestamp": None,
        "creator": dummy_user,
    }

    async def mock_post(session, payload):
        return 1

    monkeypatch.setattr(notes, "create", mock_post)

    response = notes_test_client.post(
        "/notes/", data=json.dumps(test_request_payload)
    )

    assert response.status_code == 201
    assert response.json() == test_response_payload


def test_create_note_invalid_json(notes_test_client: TestClient):
    response = notes_test_client.post(
        "/notes/", data=json.dumps({"titles": "something"})
    )
    assert response.status_code == 422


def test_read_note(notes_test_client: TestClient, monkeypatch):
    test_data = {
        "id": 1,
        "title": "something",
        "description": "something else",
        "timestamp": "2021-02-15T07:13:55.837950",
        "creator": None,
    }

    async def mock_get(session, id):
        return test_data

    monkeypatch.setattr(notes, "view", mock_get)

    response = notes_test_client.get("/notes/1")
    assert response.status_code == 200
    assert response.json() == test_data


def test_read_note_incorrect_id(notes_test_client: TestClient, monkeypatch):
    async def mock_get(session, id):
        return None

    monkeypatch.setattr(notes, "view", mock_get)

    response = notes_test_client.get("/notes/666")
    assert response.status_code == 404
    assert response.json()["detail"] == "Note with id 666 not found"


def test_read_all_notes(notes_test_client: TestClient, monkeypatch):
    test_data = [
        {
            "id": 1,
            "title": "something",
            "description": "something else",
            "timestamp": "2021-02-15T07:13:55.837950",
        },
        {
            "id": 2,
            "title": "someone",
            "description": "someone else",
            "timestamp": "2021-02-15T07:13:55.837950",
        },
    ]

    async def mock_get_all(session):
        return test_data

    monkeypatch.setattr(notes, "get_all", mock_get_all)

    response = notes_test_client.get("/notes/")
    assert response.status_code == 200
    assert response.context["data"] == test_data


def test_update_note(notes_test_client: TestClient, monkeypatch):
    test_update_data = {
        "id": 1,
        "title": "someone",
        "description": "someone else",
        "timestamp": "2021-02-15T07:13:55.837950",
    }

    async def mock_get(session, id):
        return True

    monkeypatch.setattr(notes, "view", mock_get)

    async def mock_put(session, id, payload):
        return test_update_data

    monkeypatch.setattr(notes, "update", mock_put)

    response = notes_test_client.put(
        "/notes/1/", data=json.dumps(test_update_data)
    )
    assert response.status_code == 202
    assert response.json() == test_update_data


@pytest.mark.parametrize(
    "id, payload, status_code",
    [
        [1, {}, 422],
        [1, {"description": "bar"}, 422],
        [999, {"title": "foo", "description": "bar"}, 404],
    ],
)
def test_update_note_invalid(
    notes_test_client: TestClient, monkeypatch, id, payload, status_code
):
    async def mock_get(session, id):
        return None

    monkeypatch.setattr(notes, "view", mock_get)

    response = notes_test_client.put(
        f"/notes/{id}/",
        data=json.dumps(payload),
    )
    assert response.status_code == status_code


def test_delete_note(notes_test_client: TestClient, monkeypatch):
    test_data = {
        "id": 1,
        "title": "something",
        "description": "something else",
        "timestamp": "2021-02-15T07:13:55.837950",
    }

    async def mock_get(session, id):
        return test_data

    monkeypatch.setattr(notes, "view", mock_get)

    async def mock_delete(session, id):
        return test_data

    monkeypatch.setattr(notes, "delete", mock_delete)

    response = notes_test_client.delete("/notes/1/")
    assert response.status_code == 200
    assert response.json() == test_data


def test_delete_note_incorrect_id(notes_test_client: TestClient, monkeypatch):
    async def mock_get(session, id):
        return None

    monkeypatch.setattr(notes, "view", mock_get)

    response = notes_test_client.delete("/notes/999/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Note with id 999 not found"