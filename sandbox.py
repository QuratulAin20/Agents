import docker
from config import PROJECTS_DIR, DOCKER_IMAGE, EXECUTION_TIMEOUT_SECONDS, USE_DOCKER_SANDBOX
from logger import logger

class DockerSandbox:
    def __init__(self):
        self.enabled = USE_DOCKER_SANDBOX
        if self.enabled:
            try:
                self.client = docker.from_env()
                # Test connection early
                self.client.ping()
            except Exception as e:
                logger.error(f"Docker client initialization failed. Falling back to un-isolated run. Error: {e}")
                self.enabled = False

    def execute_python_file(self, project_slug: str, relative_file_path: str) -> dict:
        """Executes a python file inside an isolated container wrapper.
        
        Returns:
            dict: Containing status (success/failure), stdout, and stderr.
        """
        target_dir = PROJECTS_DIR / project_slug
        if not target_dir.exists():
            return {"status": "error", "message": f"Project directory '{project_slug}' does not exist."}

        if not self.enabled:
            return {"status": "skipped", "message": "Docker isolation disabled or unavailable."}

        # Format host directory path to match standard POSIX configurations for Docker mounts
        host_path = str(target_dir.resolve())
        container_mount_point = "/workspace"
        command = f"python {relative_file_path}"

        logger.info(f"Spawning isolated container to run execution command: {command}")

        try:
            # Run the ephemeral container securely
            container = self.client.containers.run(
                image=DOCKER_IMAGE,
                command=command,
                volumes={host_path: {"bind": container_mount_point, "mode": "rw"}},
                working_dir=container_mount_point,
                detach=True,
                network_disabled=True, # Prevent external web request vulnerabilities
                mem_limit="256m"       # Prevent denial-of-service memory exhaustion
            )

            # Wait for execution completion with strict timeouts
            result = container.wait(timeout=EXECUTION_TIMEOUT_SECONDS)
            exit_code = result.get("StatusCode", -1)
            
            stdout = container.logs(stdout=True, stderr=False).decode("utf-8")
            stderr = container.logs(stdout=False, stderr=True).decode("utf-8")

            # Complete cleanup cleanup 
            container.remove(force=True)

            return {
                "status": "success" if exit_code == 0 else "failed",
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": stderr
            }

        except docker.errors.ContainerError as ce:
            logger.error(f"Container runtime exception encountered: {ce}")
            return {"status": "failed", "error": str(ce)}
        except Exception as e:
            logger.error(f"Execution handling failure: {e}")
            return {"status": "error", "message": str(e)}

# Export single global instance
sandbox_manager = DockerSandbox()