import docker

from config import DOCKER_IMAGE, EXECUTION_TIMEOUT_SECONDS, PROJECTS_DIR, USE_DOCKER_SANDBOX
from logger import logger


class DockerSandbox:
    def __init__(self):
        self.enabled = USE_DOCKER_SANDBOX
        if self.enabled:
            try:
                self.client = docker.from_env()
                self.client.ping()
            except Exception as e:
                logger.error(
                    f"Docker client initialization failed. Falling back to un-isolated run. Error: {e}"
                )
                self.enabled = False

    def _cleanup_container(self, container) -> None:
        if container is None:
            return
        try:
            container.remove(force=True)
        except Exception as cleanup_error:
            logger.warning(f"Container cleanup failed: {cleanup_error}")

    def execute_python_file(self, project_slug: str, relative_file_path: str) -> dict:
        """Execute a python file inside an isolated container wrapper."""
        if ".." in relative_file_path or relative_file_path.startswith(("/", "\\")):
            return {"status": "error", "message": "Invalid entrypoint path."}

        target_dir = PROJECTS_DIR / project_slug
        if not target_dir.exists():
            return {"status": "error", "message": f"Project directory '{project_slug}' does not exist."}

        if not self.enabled:
            return {"status": "skipped", "message": "Docker isolation disabled or unavailable."}

        host_path = str(target_dir.resolve())
        container_mount_point = "/workspace"
        command = f"python {relative_file_path}"

        logger.info(f"Spawning isolated container to run execution command: {command}")

        container = None
        try:
            container = self.client.containers.run(
                image=DOCKER_IMAGE,
                command=command,
                volumes={host_path: {"bind": container_mount_point, "mode": "ro"}},
                working_dir=container_mount_point,
                detach=True,
                network_disabled=True,
                mem_limit="256m",
            )

            result = container.wait(timeout=EXECUTION_TIMEOUT_SECONDS)
            exit_code = result.get("StatusCode", -1)

            stdout = container.logs(stdout=True, stderr=False).decode("utf-8")
            stderr = container.logs(stdout=False, stderr=True).decode("utf-8")

            return {
                "status": "success" if exit_code == 0 else "failed",
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": stderr,
            }

        except docker.errors.ContainerError as ce:
            logger.error(f"Container runtime exception encountered: {ce}")
            return {"status": "failed", "error": str(ce)}
        except Exception as e:
            logger.error(f"Execution handling failure: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            self._cleanup_container(container)


sandbox_manager = DockerSandbox()
