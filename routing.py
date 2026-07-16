from state import AgentState


def review_passed(content: str) -> bool:
    return "all files pass review" in content.lower()


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
    return "developer"
