"""Domain-specific tools for the developer agent."""

from __future__ import annotations

import re
from pathlib import Path

from config import PROJECTS_DIR
from logger import logger
from sandbox import sandbox_manager


def validate_project_path(project_slug: str, file_name: str) -> tuple[Path | None, str | None]:
    """Validate and resolve a project file path under PROJECTS_DIR."""
    slug = project_slug.strip()
    name = file_name.strip()

    if not slug or not name:
        return None, "Error: project_slug and file_name are required."

    if ".." in slug or ".." in name or slug.startswith(("/", "\\")) or name.startswith(("/", "\\")):
        return None, "Error: path traversal is not allowed."

    if Path(slug).is_absolute() or Path(name).is_absolute():
        return None, "Error: absolute paths are not allowed."

    target_dir = (PROJECTS_DIR / slug).resolve()
    target_file = (target_dir / name).resolve()

    try:
        target_file.relative_to(PROJECTS_DIR.resolve())
    except ValueError:
        return None, "Error: path escapes the projects workspace."

    return target_file, None


def name_project(project_name: str) -> str:
    """Create a project folder with the given name. Must be called FIRST."""
    slug = project_name.lower().strip()
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"[^a-z0-9\-]", "", slug)
    slug = slug.strip("-")

    if not slug:
        return "Error: Could not create a valid project name."

    project_path = PROJECTS_DIR / slug
    project_path.mkdir(parents=True, exist_ok=True)
    return f"Project folder created: {slug}/"


def write_project_file(project_slug: str, file_name: str, content: str) -> str:
    """Create or overwrite a file inside a specific project workspace."""
    try:
        target_file, error = validate_project_path(project_slug, file_name)
        if error:
            return error

        target_file.parent.mkdir(parents=True, exist_ok=True)
        target_file.write_text(content, encoding="utf-8")
        return f"Successfully created/updated file: {project_slug.strip()}/{file_name.strip()}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


def test_project_code(project_slug: str, entrypoint_file: str) -> str:
    """Safely run project code inside an isolated Docker sandbox container."""
    try:
        _, error = validate_project_path(project_slug, entrypoint_file)
        if error:
            return error

        logger.info(f"Agent requested sandbox run on {project_slug}/{entrypoint_file}")
        result = sandbox_manager.execute_python_file(
            project_slug=project_slug.strip(),
            relative_file_path=entrypoint_file.strip(),
        )

        status = result.get("status", "unknown")
        if status == "success":
            return f"Sandbox Run PASS!\nOutput:\n{result.get('stdout', '')}"
        if status == "failed":
            return (
                f"Sandbox Run CRASHED (Exit Code {result.get('exit_code')})!\n"
                f"STDOUT:\n{result.get('stdout', '')}\n"
                f"STDERR:\n{result.get('stderr', '')}"
            )
        return f"Sandbox failed to initialize or execute: {result.get('message', 'Unknown error')}"
    except Exception as e:
        return f"Sandbox wrapper tool exception: {str(e)}"


TOOLS_MAP = {
    "name_project": name_project,
    "write_project_file": write_project_file,
    "test_project_code": test_project_code,
}
