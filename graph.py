"""LangGraph workflow routing user queries to specialist agents."""

from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from agents.supervisor import supervisor_node, route_after_supervisor
from agents.holiday_agent import holiday_agent_node
from agents.hr_agent import hr_agent_node
from agents.events_agent import events_agent_node
from agents.team_agent import team_agent_node
from agents.general_agent import general_agent_node


class AgentState(TypedDict):
    """Conversation state shared between graph nodes."""

    messages: Annotated[list[BaseMessage], add_messages]
    next_agent: str


SPECIALIST_NODES = (
    "holiday_agent",
    "hr_agent",
    "events_agent",
    "team_agent",
    "general_agent",
)


def create_company_assistant_graph():
    """Build supervisor-specialist routing workflow.

    Returns:
        Compiled LangGraph with memory checkpointing by thread_id.
    """
    graph = StateGraph(AgentState)

    # Add supervisor and specialist nodes
    graph.add_node("supervisor", supervisor_node)
    for name in SPECIALIST_NODES:
        graph.add_node(name, eval(f"{name}_node"))

    # Supervisor is entry point, routes to specialist, specialist returns END
    graph.set_entry_point("supervisor")
    graph.add_conditional_edges(
        "supervisor",
        route_after_supervisor,
        {name: name for name in SPECIALIST_NODES},
    )
    for name in SPECIALIST_NODES:
        graph.add_edge(name, END)

    return graph.compile(checkpointer=MemorySaver())


company_assistant = create_company_assistant_graph()


async def run_agent_graph(user_query: str, thread_id: str = "default") -> tuple[str, str]:
    """Execute one query through the agent graph.

    Args:
        user_query: User's question or input.
        thread_id: Conversation identifier for memory continuity.

    Returns:
        Tuple of (response_text, agent_name).
    """
    config = {"configurable": {"thread_id": thread_id}}
    result = await company_assistant.ainvoke(
        {"messages": [HumanMessage(content=user_query)]},
        config=config,
    )

    # Extract the latest AI message and its agent name
    for msg in reversed(result.get("messages", [])):
        if isinstance(msg, AIMessage):
            agent_key = str(msg.name or "assistant")
            return str(msg.content), agent_key

    return "Unable to generate response.", "unknown"
