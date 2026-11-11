"""Offline tests for supervisor routing, specialist dispatch and continuity.

A fake chat model replaces Gemini so no network or API key is needed.
"""

import asyncio
from typing import Any

import pytest
from langchain_core.language_models.fake_chat_models import FakeListChatModel

import graph as graph_module
from agents import supervisor as supervisor_module
from config import settings as settings_module


def _make_llm_factory(responses: list[str]):
    """Return a get_llm replacement that shares one scripted model across calls.

    Sharing the instance lets the supervisor and specialist consume the
    replies in order.
    """
    llm = FakeListChatModel(responses=responses)

    def factory() -> FakeListChatModel:
        return llm

    return factory


def _run(query: str, thread_id: str) -> tuple[str, str]:
    """Run one query through the graph synchronously."""
    return asyncio.run(graph_module.run_agent_graph(query, thread_id))


@pytest.fixture
def fake_llm(monkeypatch: pytest.MonkeyPatch):
    """Patch settings.get_llm; tests set the reply sequence via the returned setter."""

    def set_responses(responses: list[str]) -> None:
        monkeypatch.setattr(settings_module.settings, "get_llm", _make_llm_factory(responses))

    set_responses(["general_agent", "Fake answer"])
    return set_responses


def test_supervisor_routes_holiday_query(fake_llm) -> None:
    """A holiday question should be answered by holiday_agent."""
    fake_llm(["holiday_agent", "Holiday answer"])
    response, agent = _run("What are our upcoming holidays?", "t-holiday")
    assert agent == "holiday_agent"
    assert response == "Holiday answer"


def test_supervisor_routes_hr_query(fake_llm) -> None:
    """A leave question should be answered by hr_agent."""
    fake_llm(["hr_agent", "HR answer"])
    _, agent = _run("What is our leave policy?", "t-hr")
    assert agent == "hr_agent"


def test_supervisor_routes_team_query(fake_llm) -> None:
    """A team question should be answered by team_agent."""
    fake_llm(["team_agent", "Team answer"])
    _, agent = _run("Which team handles AI development?", "t-team")
    assert agent == "team_agent"


def test_invalid_supervisor_output_falls_back_to_general(fake_llm) -> None:
    """Unknown routing labels must fall back to general_agent."""
    fake_llm(["not_a_real_agent", "General answer"])
    response, agent = _run("Tell me something", "t-fallback")
    assert agent == "general_agent"
    assert response == "General answer"


def test_only_one_specialist_runs_per_query(fake_llm) -> None:
    """The supervisor call plus exactly one specialist call should happen."""
    fake_llm(["events_agent", "Events answer"])
    calls: list[str] = []
    original = settings_module.settings.get_llm

    def counting_factory():
        calls.append("llm")
        return original()

    settings_module.settings.get_llm = counting_factory
    try:
        _, agent = _run("What events are coming up?", "t-single")
    finally:
        settings_module.settings.get_llm = original
    assert agent == "events_agent"
    assert len(calls) == 2


def test_conversation_continuity_same_thread(fake_llm) -> None:
    """Messages from earlier turns on the same thread_id remain in state."""
    fake_llm(["general_agent", "First", "general_agent", "Second"])
    _run("Hello there", "t-continuity")
    _run("And another question", "t-continuity")

    snapshot = graph_module.company_assistant.get_state(
        {"configurable": {"thread_id": "t-continuity"}}
    )
    contents = [str(m.content) for m in snapshot.values["messages"]]
    assert "Hello there" in contents
    assert "And another question" in contents


def test_separate_threads_are_isolated(fake_llm) -> None:
    """Different thread_ids must not share conversation history."""
    fake_llm(["general_agent", "A", "general_agent", "B"])
    _run("Thread A question", "t-iso-a")
    _run("Thread B question", "t-iso-b")

    snapshot = graph_module.company_assistant.get_state(
        {"configurable": {"thread_id": "t-iso-b"}}
    )
    contents = [str(m.content) for m in snapshot.values["messages"]]
    assert "Thread A question" not in contents


def test_supervisor_node_empty_state_defaults_to_general() -> None:
    """With no user message the supervisor must not call the LLM."""
    result = asyncio.run(supervisor_module.supervisor_node({"messages": []}))
    assert result == {"next_agent": "general_agent"}
