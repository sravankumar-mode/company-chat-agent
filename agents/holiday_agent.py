"""Holiday specialist agent for company holiday queries."""

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from tools.company_tools import HolidayTools
from config.settings import settings


PROMPT = """You are a company holiday specialist.
Answer questions about company holidays, working days, and holiday calendars.
Provide clear dates and distinguish between national and optional holidays."""


async def holiday_agent_node(state: dict) -> dict:
    """Answer holiday and working day queries."""
    messages = state.get("messages", [])
    if not messages:
        return {}

    last_message = messages[-1]
    user_query = last_message.content if isinstance(last_message, BaseMessage) else str(last_message)

    # Get holiday data
    holidays_info = HolidayTools.get_upcoming_holidays()

    # Call LLM with context
    llm = settings.get_llm()
    response = await llm.ainvoke([
        SystemMessage(content=PROMPT),
        HumanMessage(content=f"Holidays:\n{holidays_info}\n\nQuestion: {user_query}"),
    ])

    return {"messages": [AIMessage(content=response.content, name="holiday_agent")]}
