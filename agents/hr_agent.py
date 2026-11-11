"""HR specialist agent for HR policies and leave queries."""

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from tools.company_tools import HRTools
from config.settings import settings


PROMPT = """You are a company HR specialist.
Answer questions about leave policies, leave balances, HR policies, benefits, and working hours.
Be empathetic and provide clear policy information."""


async def hr_agent_node(state: dict) -> dict:
    """Answer HR policy and leave-related queries."""
    messages = state.get("messages", [])
    if not messages:
        return {}

    last_message = messages[-1]
    user_query = last_message.content if isinstance(last_message, BaseMessage) else str(last_message)

    # Get HR policy data
    policy_info = HRTools.get_leave_policy()

    # Call LLM with context
    llm = settings.get_llm()
    response = await llm.ainvoke([
        SystemMessage(content=PROMPT),
        HumanMessage(content=f"HR Policies:\n{policy_info}\n\nQuestion: {user_query}"),
    ])

    return {"messages": [AIMessage(content=response.content, name="hr_agent")]}
