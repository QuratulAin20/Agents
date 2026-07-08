"""Domain-specific tools for the primary agent."""

import re
from pathlib import Path
from config import PROJECTS_DIR
from logger import logger
from sandbox import sandbox_manager

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

def execute_project_code(project_slug: str, main_script_name: str = "main.py") -> str:
    """Securely execute a script inside the project workspace to evaluate output results.

    Use this tool to test written python scripts before handing them off to the reviewer.
    It returns execution outcomes, outputs, or error traces.

    Args:
        project_slug: The exact short name/slug folder of the target project.
        main_script_name: The script file to run (default is 'main.py').
    """
    logger.info(f"Agent requested execution run on {project_slug}/{main_script_name}")
    
    run_report = sandbox_manager.execute_python_file(project_slug, main_script_name)
    
    if run_report["status"] == "success":
        return f"Execution SUCCESS!\n--- Standard Output ---\n{run_report['stdout']}"
    elif run_report["status"] == "failed":
        return (
            f"Execution FAILED with exit code {run_report.get('exit_code')}\n"
            f"--- Standard Error Stream ---\n{run_report.get('stderr')}\n"
            f"--- Standard Output Stream ---\n{run_report.get('stdout')}"
        )
    else:
        return f"Execution aborted or unavailable: {run_report.get('message')}"