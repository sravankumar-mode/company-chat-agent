"""Offline tests for the Google Chat endpoint: auth, event handling and errors.

Google's token verification is replaced at the network boundary and the LLM is
faked, so the real LangGraph workflow runs without network or API keys.
"""

import asyncio

import pytest
from fastapi.testclient import TestClient
from langchain_core.language_models.fake_chat_models import FakeListChatModel

import google_chat
from api import app
from config import settings as settings_module
from graph import company_assistant


AUDIENCE = "https://example-service.run.app/google-chat"
AUTH = {"Authorization": "Bearer good-token"}


def _fake_oauth_verify(token, request, audience=None, **kwargs):
    """Accept only the good token for the configured endpoint audience."""
    if token != "good-token" or audience != AUDIENCE:
        raise ValueError("Token verification failed")
    return {"email": google_chat.CHAT_ISSUER, "email_verified": True}


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setattr(settings_module.settings, "google_chat_audience", AUDIENCE)
    monkeypatch.setattr(google_chat.id_token, "verify_oauth2_token", _fake_oauth_verify)
    return TestClient(app)


@pytest.fixture
def fake_llm(monkeypatch: pytest.MonkeyPatch):
    """Script the supervisor and specialist replies for one test."""

    def set_responses(responses: list[str]) -> None:
        llm = FakeListChatModel(responses=responses)
        monkeypatch.setattr(settings_module.settings, "get_llm", lambda: llm)

    set_responses(["general_agent", "Fake answer"])
    return set_responses


def _message_event(text: str, space: str = "spaces/AAA", user: str = "users/123") -> dict:
    return {
        "type": "MESSAGE",
        "message": {"text": f"@Company AI {text}", "argumentText": f" {text}"},
        "space": {"name": space, "type": "ROOM"},
        "user": {"name": user, "displayName": "Test Employee"},
    }


def test_message_event_is_answered_by_langgraph(client, fake_llm) -> None:
    """A MESSAGE event goes through the supervisor and specialist, and the reply is returned."""
    fake_llm(["hr_agent", "Leave answer"])

    response = client.post("/google-chat", json=_message_event("What is our leave policy?"), headers=AUTH)

    assert response.status_code == 200
    assert response.json() == {"text": "Leave answer"}
    snapshot = company_assistant.get_state({"configurable": {"thread_id": "gchat:spaces/AAA:users/123"}})
    contents = [str(m.content) for m in snapshot.values["messages"]]
    assert "What is our leave policy?" in contents


def test_added_to_space_returns_welcome_message(client) -> None:
    """ADDED_TO_SPACE returns a welcome text without calling the LLM."""
    event = {"type": "ADDED_TO_SPACE", "space": {"name": "spaces/AAA"}, "user": {"name": "users/123"}}

    response = client.post("/google-chat", json=event, headers=AUTH)

    assert response.status_code == 200
    assert "Company AI Assistant" in response.json()["text"]


def test_removed_from_space_returns_empty_response(client) -> None:
    """REMOVED_FROM_SPACE acknowledges with an empty body and clears that user's memory."""
    event = {"type": "REMOVED_FROM_SPACE", "space": {"name": "spaces/AAA"}, "user": {"name": "users/123"}}

    response = client.post("/google-chat", json=event, headers=AUTH)

    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.parametrize(
    "headers",
    [{}, {"Authorization": "Basic abc"}, {"Authorization": "Bearer bad-token"}],
    ids=["missing", "wrong-scheme", "invalid-token"],
)
def test_missing_or_invalid_token_is_rejected(client, fake_llm, headers) -> None:
    """Requests without a valid Google-issued bearer token get 401 and never reach the graph."""
    fake_llm([])

    response = client.post("/google-chat", json=_message_event("hello"), headers=headers)

    assert response.status_code == 401


def test_endpoint_audience_requires_chat_issuer(monkeypatch) -> None:
    """A valid Google ID token from another service account must not be accepted."""
    monkeypatch.setattr(
        google_chat.id_token,
        "verify_oauth2_token",
        lambda *a, **k: {"email": "attacker@example.com", "email_verified": True},
    )

    assert google_chat.verify_google_chat_token("Bearer token", AUDIENCE) is False


def test_project_number_audience_checks_jwt_issuer(monkeypatch) -> None:
    """Numeric audiences use the self-signed JWT flow and check the chat issuer."""
    calls = []

    def fake_verify_token(token, request, audience=None, certs_url=None, **kwargs):
        calls.append((audience, certs_url))
        return {"iss": google_chat.CHAT_ISSUER if token == "good" else "evil@example.com"}

    monkeypatch.setattr(google_chat.id_token, "verify_token", fake_verify_token)

    assert google_chat.verify_google_chat_token("Bearer good", "1234567890") is True
    assert google_chat.verify_google_chat_token("Bearer evil", "1234567890") is False
    assert calls[0] == ("1234567890", google_chat.CHAT_CERTS_URL)


def test_unconfigured_audience_fails_closed(client, monkeypatch, fake_llm) -> None:
    """Without GOOGLE_CHAT_AUDIENCE the endpoint refuses every request."""
    monkeypatch.setattr(settings_module.settings, "google_chat_audience", "")
    fake_llm([])

    response = client.post("/google-chat", json=_message_event("hello"), headers=AUTH)

    assert response.status_code == 500


def test_malformed_json_returns_400(client) -> None:
    """A verified request with a non-JSON body is rejected with 400."""
    response = client.post(
        "/google-chat", content=b"not json", headers={**AUTH, "Content-Type": "application/json"}
    )

    assert response.status_code == 400


def test_graph_error_returns_friendly_text_without_details(client, monkeypatch) -> None:
    """Unexpected failures return a safe Chat reply and do not expose the exception text."""

    async def failing_graph(**kwargs):
        raise RuntimeError("secret-internal-detail")

    monkeypatch.setattr(google_chat, "run_agent_graph", failing_graph)

    response = client.post("/google-chat", json=_message_event("hello"), headers=AUTH)

    assert response.status_code == 200
    assert response.json()["text"] == google_chat.ERROR_TEXT
    assert "secret-internal-detail" not in response.text


def test_slow_graph_returns_timeout_text(client, monkeypatch) -> None:
    """Responses that exceed the Chat synchronous deadline get a timeout reply."""

    async def slow_graph(**kwargs):
        await asyncio.sleep(1)
        return "too late", "general_agent"

    monkeypatch.setattr(google_chat, "run_agent_graph", slow_graph)
    monkeypatch.setattr(google_chat, "RESPONSE_TIMEOUT_SECONDS", 0.01)

    response = client.post("/google-chat", json=_message_event("hello"), headers=AUTH)

    assert response.json() == {"text": google_chat.TIMEOUT_TEXT}
