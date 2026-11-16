from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app
from app.platforms.base import PostReceipt
from app.services.posting_service import PostingService


class SuccessfulPoster:
    name = "Working"

    async def post(self, message, client):
        return PostReceipt("https://social.example/post/1", True)


class FailingPoster:
    name = "Unavailable"

    async def post(self, message, client):
        raise RuntimeError("Authentication failed")


def test_posting_continues_when_one_platform_fails():
    with TestClient(app) as client:
        app.state.posting_service = PostingService([SuccessfulPoster(), FailingPoster()])
        response = client.post(
            "/posting",
            json={"message": "Hello https://example.com"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert [item["status"] for item in body["results"]] == ["success", "failed"]
    assert body["results"][0]["posted_url"] == "https://social.example/post/1"
    assert body["results"][1]["error"] == "Authentication failed"
    assert body["results"][0]["date"] == datetime.now(timezone.utc).date().isoformat()


def test_rejects_message_over_200_characters():
    with TestClient(app) as client:
        response = client.post("/posting", json={"message": "x" * 201})

    assert response.status_code == 422


def test_rejects_missing_or_multiple_links():
    with TestClient(app) as client:
        missing = client.post("/posting", json={"message": "No link here"})
        multiple = client.post(
            "/posting",
            json={"message": "https://one.example https://two.example"},
        )

    assert missing.status_code == 422
    assert multiple.status_code == 422


def test_rejects_invalid_url():
    with TestClient(app) as client:
        response = client.post("/posting", json={"message": "Visit https://"})

    assert response.status_code == 422
