"""Explicit Multi-Agent Deep Loop framework with Workspace Tools & Code Reviewer Sub-nodes."""

import json
from pathlib import Path
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage, SystemMessage, ToolMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

from config import PROJECTS_DIR, GOOGLE_MODEL, MAX_RETRIES, REQUEST_TIMEOUT
from sandbox import sandbox_manager # Ensure your sandbox.py file exposes this

# =====================================================================
# State & Hardened Disk Tools Definition
# =====================================================================

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    review_completed: bool  # Flag to break loops and prevent infinite rewriting

def write_project_file(project_slug: str, file_name: str, content: str) -> str:
    """Create or overwrite a file inside a specific project workspace."""
    try:
        target_dir = Path(PROJECTS_DIR) / project_slug.strip()
        target_dir.mkdir(parents=True, exist_ok=True)
        with open(target_dir / file_name.strip(), "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully created/updated file: {project_slug}/{file_name}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

def test_project_code(project_slug: str, entrypoint_file: str) -> str:
    """Safely runs the written project code inside an isolated Docker sandbox container.
    
    Args:
        project_slug: The folder name of the project.
        entrypoint_file: The main file to execute (e.g., 'main.py').
    """
    try:
        # Call your actual sandbox method
        result = sandbox_manager.execute_python_file(
            project_slug=project_slug.strip(), 
            relative_file_path=entrypoint_file.strip()
        )
        
        status = result.get("status", "unknown")
        
        if status == "success":
            return f"Sandbox Run PASS!\nOutput:\n{result.get('stdout', '')}"
        elif status == "failed":
            return f"Sandbox Run CRASHED (Exit Code {result.get('exit_code')})!\nSTDOUT:\n{result.get('stdout', '')}\nSTDERR:\n{result.get('stderr', '')}"
        else:
            # Catch skipped or error statuses safely
            return f"Sandbox failed to initialize or execute: {result.get('message', 'Unknown error')}"
            
    except Exception as e:
        return f"Sandbox wrapper tool exception: {str(e)}"

TOOLS_MAP = {
    "write_project_file": write_project_file,
    "test_project_code": test_project_code
}

# =====================================================================
# Hardened Prompts & Models Setup
# =====================================================================

DEV_SYSTEM_PROMPT = """You are an expert senior Python developer. 
1. Use 'write_project_file' to build out scripts (main.py, README.md).
2. Use 'test_project_code' to test your execution. If it crashes, rewrite files to fix bugs.
3. Once code passes sandbox runs, stop calling tools so your work can be audited by the reviewer."""

REVIEWER_SYSTEM_PROMPT = """You are an expert automated QA Code Reviewer. 
Analyze the chat history and code files written above. Check for logic bugs, missing documentation, or bad styling.
If everything is perfect, output: 'All files pass review — code is ready for delivery.'
If there are issues, list them explicitly so the developer agent knows what to fix."""

llm_model = ChatGoogleGenerativeAI(
    model=GOOGLE_MODEL, max_retries=MAX_RETRIES, timeout=REQUEST_TIMEOUT, convert_system_message_to_human=True
)

dev_agent = llm_model.bind_tools([write_project_file, test_project_code])
reviewer_agent = llm_model # No tools needed for basic critical evaluation

# =====================================================================
# State Graph Logic Nodes
# =====================================================================

def call_developer(state: AgentState) -> dict:
    messages = [SystemMessage(content=DEV_SYSTEM_PROMPT)] + [m for m in state["messages"] if not isinstance(m, SystemMessage)]
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
                tool_messages.append(ToolMessage(content=result, tool_call_id=tool_call["id"], name=tool_name))
    return {"messages": tool_messages}

def call_reviewer(state: AgentState) -> dict:
    """Active subagent node that intercepts state history to perform an audit."""
    # Strip old system messages to inject the Reviewer identity cleanly
    history = [m for m in state["messages"] if not isinstance(m, SystemMessage)]
    messages = [SystemMessage(content=REVIEWER_SYSTEM_PROMPT)] + history + [HumanMessage(content="Perform your review now.")]
    
    response = reviewer_agent.invoke(messages)
    
    # Check if the reviewer gave an explicit stamp of approval
    passed = "all files pass review" in response.content.lower()
    return {"messages": [response], "review_completed": passed}

# =====================================================================
# Routing Edge Logic
# =====================================================================

def route_after_dev(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    if state.get("review_completed"):
        return "deliver"
    return "review"

def route_after_review(state: AgentState) -> str:
    if state.get("review_completed"):
        return "deliver"
    return "developer" # Send back to developer node to execute fixes!

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
    
    workflow.add_conditional_edges("developer", route_after_dev, {"tools": "execute_tools", "review": "reviewer", "deliver": END})
    workflow.add_conditional_edges("reviewer", route_after_review, {"developer": "developer", "deliver": END})
    
    checkpointer = MemorySaver()
    return workflow.compile(checkpointer=checkpointer)