"""General specialist agent for general company queries."""

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from config.settings import settings


PROMPT = """You are a general company information specialist.
Answer general company questions about vision, culture, history, and company-related matters.
If a question would be better handled by another department, suggest it."""


async def general_agent_node(state: dict) -> dict:
    """Answer general company queries."""
    messages = state.get("messages", [])
    if not messages:
        return {}

    last_message = messages[-1]
    user_query = last_message.content if isinstance(last_message, BaseMessage) else str(last_message)

    # Call LLM
    llm = settings.get_llm()
    response = await llm.ainvoke([
        SystemMessage(content=PROMPT),
        HumanMessage(content=user_query),
    ])

    return {"messages": [AIMessage(content=response.content, name="general_agent")]}
