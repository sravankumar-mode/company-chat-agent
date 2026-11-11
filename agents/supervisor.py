"""Supervisor agent routing logic and display names."""

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from config.settings import settings


SUPERVISOR_PROMPT = """Route this user query to ONE specialist agent:

- holiday_agent: Company holidays, working days, holiday calendars
- hr_agent: Leave policies, leave balances, HR policies, working hours
- events_agent: Company events, team events, announcements
- team_agent: Employees, teams, departments, organizational structure
- general_agent: General company questions not fitting other categories

Respond with ONLY the agent name and nothing else.

Examples:
- "What are our upcoming holidays?" -> holiday_agent
- "How many days of leave do I have?" -> hr_agent
- "When is the team building event?" -> events_agent
- "Who is in the backend team?" -> team_agent
- "What is the company vision?" -> general_agent
"""

SPECIALIST_NAMES = (
    "holiday_agent",
    "hr_agent",
    "events_agent",
    "team_agent",
    "general_agent",
)

# Agent display names shown to users
AGENT_DISPLAY_NAMES = {
    "holiday_agent": "Holiday Agent (Agent)",
    "hr_agent": "HR Agent (Agent)",
    "events_agent": "Events Agent (Agent)",
    "team_agent": "Team Agent (Agent)",
    "general_agent": "General Agent (Agent)",
}


def _get_latest_user_message(messages: list[BaseMessage]) -> str:
    """Extract the most recent user message text."""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            return str(msg.content)
    return ""


async def supervisor_node(state: dict) -> dict:
    """Route user query to appropriate specialist agent."""
    user_query = _get_latest_user_message(state.get("messages", []))
    if not user_query:
        return {"next_agent": "general_agent"}

    # Get LLM and classify query
    llm = settings.get_llm()
    response = await llm.ainvoke([
        SystemMessage(content=SUPERVISOR_PROMPT),
        HumanMessage(content=user_query),
    ])

    # Extract agent name and validate
    agent_name = str(response.content).strip().strip("`'\" .").lower()
    if agent_name not in SPECIALIST_NAMES:
        agent_name = "general_agent"

    return {"next_agent": agent_name}


def route_after_supervisor(state: dict) -> str:
    """Return the next agent node name."""
    next_agent = state.get("next_agent", "general_agent")
    return next_agent if next_agent in SPECIALIST_NAMES else "general_agent"
