from langchain_core.messages import AIMessage

from routing import route_after_dev, route_after_review
from tools import validate_project_path, write_project_file


def test_validate_project_path_accepts_valid_path(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.PROJECTS_DIR", tmp_path)
    path, error = validate_project_path("sales-report", "main.py")
    assert error is None
    assert path == tmp_path / "sales-report" / "main.py"


def test_validate_project_path_rejects_traversal(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.PROJECTS_DIR", tmp_path)
    _, error = validate_project_path("sales-report", "../secrets.env")
    assert error is not None
    assert "path traversal" in error.lower()


def test_write_project_file_rejects_escape(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.PROJECTS_DIR", tmp_path)
    result = write_project_file("demo", "../../outside.py", "print('nope')")
    assert "path traversal" in result.lower()


def test_route_after_dev_routes_to_tools():
    message = AIMessage(content="", tool_calls=[{"name": "write_project_file", "args": {}, "id": "1"}])
    assert route_after_dev({"messages": [message]}) == "tools"


def test_route_after_review_routes_back_to_developer():
    assert route_after_review({"review_completed": False, "review_cycles": 1}) == "developer"


def test_route_after_review_delivers_when_complete():
    assert route_after_review({"review_completed": True, "review_cycles": 2}) == "deliver"
