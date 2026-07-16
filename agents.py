"""Explicit Multi-Agent Deep Loop framework with Workspace Tools & Code Reviewer Sub-nodes."""

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from config import GOOGLE_MODEL, MAX_RETRIES, MAX_REVIEW_CYCLES, REQUEST_TIMEOUT
from routing import review_passed, route_after_dev, route_after_review
from state import AgentState
from tools import TOOLS_MAP, name_project, test_project_code, write_project_file
# =====================================================================
# Prompts & Models
# =====================================================================

DEV_SYSTEM_PROMPT = """You are an expert senior Python developer.
1. Use 'name_project' first to create a project folder slug.
2. Use 'write_project_file' to build scripts (main.py, README.md, sample data files).
3. Use only Python standard library modules (no pip packages). The sandbox runs python:3.11-slim with no network access.
4. Use 'test_project_code' to test execution. If it crashes, rewrite files to fix bugs.
5. Once code passes sandbox runs, stop calling tools so your work can be audited by the reviewer."""

REVIEWER_SYSTEM_PROMPT = """You are an expert automated QA Code Reviewer.
Analyze the chat history and code files written above. Check for logic bugs, missing documentation, or bad styling.
If everything is perfect, output exactly: 'All files pass review — code is ready for delivery.'
If there are issues, list them explicitly so the developer agent knows what to fix."""

llm_model = ChatGoogleGenerativeAI(
    model=GOOGLE_MODEL,
    max_retries=MAX_RETRIES,
    timeout=REQUEST_TIMEOUT,
    convert_system_message_to_human=True,
)

dev_agent = llm_model.bind_tools([name_project, write_project_file, test_project_code])
reviewer_agent = llm_model


# =====================================================================
# Graph Nodes
# =====================================================================


def call_developer(state: AgentState) -> dict:
    messages = [SystemMessage(content=DEV_SYSTEM_PROMPT)] + [
        m for m in state["messages"] if not isinstance(m, SystemMessage)
    ]
    response = dev_agent.invoke(messages)
    return {"messages": [response]}


def execute_tools(state: AgentState) -> dict:
    last_message = state["messages"][-1]
    tool_messages = []
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            if tool_name in TOOLS_MAP:
                result = TOOLS_MAP[tool_name](**tool_call["args"])
                tool_messages.append(
                    ToolMessage(content=result, tool_call_id=tool_call["id"], name=tool_name)
                )
    return {"messages": tool_messages}


def call_reviewer(state: AgentState) -> dict:
    history = [m for m in state["messages"] if not isinstance(m, SystemMessage)]
    messages = (
        [SystemMessage(content=REVIEWER_SYSTEM_PROMPT)]
        + history
        + [HumanMessage(content="Perform your review now.")]
    )

    response = reviewer_agent.invoke(messages)
    passed = review_passed(response.content)
    cycles = state.get("review_cycles", 0)

    if not passed:
        cycles += 1

    if not passed and cycles >= MAX_REVIEW_CYCLES:
        abort_message = AIMessage(
            content=(
                f"Maximum review cycles ({MAX_REVIEW_CYCLES}) reached. "
                "Stopping the review loop and delivering the current code."
            )
        )
        return {
            "messages": [response, abort_message],
            "review_completed": True,
            "review_cycles": cycles,
        }

    return {"messages": [response], "review_completed": passed, "review_cycles": cycles}


# =====================================================================
# Pipeline Construction
# =====================================================================


def build_agent():
    workflow = StateGraph(AgentState)

    workflow.add_node("developer", call_developer)
    workflow.add_node("execute_tools", execute_tools)
    workflow.add_node("reviewer", call_reviewer)

    workflow.add_edge(START, "developer")
    workflow.add_edge("execute_tools", "developer")

    workflow.add_conditional_edges(
        "developer",
        route_after_dev,
        {"tools": "execute_tools", "review": "reviewer", "deliver": END},
    )
    workflow.add_conditional_edges(
        "reviewer",
        route_after_review,
        {"developer": "developer", "deliver": END},
    )

    checkpointer = MemorySaver()
    return workflow.compile(checkpointer=checkpointer)
