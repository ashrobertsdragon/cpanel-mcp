import subprocess

from cpanel_mcp.connectors.cpanel_connection import CpanelConnect, Params
from cpanel_mcp.models import CpanelSSHConfig

"""cPanel SSH connector implementation."""


class CpanelSSH(CpanelConnect):
    """Connects to the cPanel account via SSH & makes UAPI function calls."""

    def __init__(self) -> None:
        """Initialize the CpanelSSH connector."""
        self._config = CpanelSSHConfig()

    def _client(self, cmd: str) -> subprocess.CompletedProcess[str]:
        key_path = self._config.ssh_key_path.replace("\\", "/")
        return subprocess.run(
            [
                "ssh",
                "-o",
                "BatchMode=yes",
                "-o",
                "StrictHostKeyChecking=accept-new",
                "-p",
                "21098",
                "-i",
                key_path,
                "-p",
                str(self._config.ssh_port),
                f"{self._config.cpanel_username}@{self._config.server_ip}",
                cmd,
            ],
            capture_output=True,
            text=True,
        )

    def make_call(
        self,
        module: str,
        function: str,
        params: Params | None = None,
    ) -> dict[str, str]:
        """Make a call to the cPanel UAPI using SSH.

        Args:
            module (str): The cPanel UAPI module (e.g., "Email").
            function (str): The function to call (e.g., "add_pop").
            params (Params | None): The parameters to pass for the API call.

        Returns:
            dict[str, str]: The response from the api.
        """
        if params is None:
            params = {}

        command = f"uapi {module} {function} {params}"

        try:
            response = self._client(command)
            if (
                response.returncode != 0
                and " Can't create the symlink for multishells"
                not in response.stderr
            ):
                return {"stderror": response.stderr + response.stdout or ""}
            return {"response": response.stdout}
        except Exception as e:
            return {"error": f"Unknown error occurred: {e}"}
