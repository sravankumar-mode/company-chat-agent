"""Team specialist agent for employee and organizational queries."""

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from tools.company_tools import TeamTools
from config.settings import settings


PROMPT = """You are a company team and employee specialist.
Answer questions about employees, teams, departments, and organizational structure.
Provide clear organizational information and relevant contact details."""


async def team_agent_node(state: dict) -> dict:
    """Answer team and employee information queries."""
    messages = state.get("messages", [])
    if not messages:
        return {}

    last_message = messages[-1]
    user_query = last_message.content if isinstance(last_message, BaseMessage) else str(last_message)

    # Get team/organization data
    team_info = TeamTools.get_team_members("Engineering")  # Default team

    # Call LLM with context
    llm = settings.get_llm()
    response = await llm.ainvoke([
        SystemMessage(content=PROMPT),
        HumanMessage(content=f"Team Info:\n{team_info}\n\nQuestion: {user_query}"),
    ])

    return {"messages": [AIMessage(content=response.content, name="team_agent")]}
