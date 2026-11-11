"""Events specialist agent for company events queries."""

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from tools.company_tools import EventTools
from config.settings import settings


PROMPT = """You are a company events specialist.
Answer questions about company events, dates, times, locations, and event types.
Provide clear details and encourage participation."""


async def events_agent_node(state: dict) -> dict:
    """Answer company event queries."""
    messages = state.get("messages", [])
    if not messages:
        return {}

    last_message = messages[-1]
    user_query = last_message.content if isinstance(last_message, BaseMessage) else str(last_message)

    # Get events data
    events_info = EventTools.get_upcoming_events()

    # Call LLM with context
    llm = settings.get_llm()
    response = await llm.ainvoke([
        SystemMessage(content=PROMPT),
        HumanMessage(content=f"Events:\n{events_info}\n\nQuestion: {user_query}"),
    ])

    return {"messages": [AIMessage(content=response.content, name="events_agent")]}
