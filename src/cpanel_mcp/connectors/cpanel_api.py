import httpx

from cpanel_mcp.connectors.cpanel_connection import CpanelConnect, Params
from cpanel_mcp.models import CpanelAPIConfig

"""cPanel API connector implementation."""


class CpanelAPI(CpanelConnect):
    """Connects to the cPanel account via API token & makes function calls."""

    def __init__(self) -> None:
        """Initialize the CpanelAPI connector."""
        self._config = CpanelAPIConfig()
        protocol = "https" if self._config.ssl else "http"
        self._base_url = (
            f"{protocol}://{self._config.hostname}:{self._config.port}"
        )
        self._client = httpx.Client(timeout=30.0)
        _auth = (
            f"cpanel {self._config.cpanel_username}:{self._config.api_token}"
        )
        self._headers = {
            "Authorization": _auth,
        }

    def make_call(
        self,
        module: str,
        function: str,
        params: Params | None = None,
    ) -> dict[str, str]:
        """Make a call to the cPanel UAPI using httpx.

        Args:
            module (str): The cPanel UAPI module (e.g., "Email").
            function (str): The function to call (e.g., "add_pop").
            params (Params | None): The parameters to pass for the API call.

        Returns:
            dict[str, str]: The JSON response from the api.
        """
        if params is None:
            params = {}

        url = f"{self._base_url}/execute/{module}/{function}"
        print(url)
        print(params)
        try:
            response = self._client.get(
                url=url, headers=self._headers, params=params
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP {e.response.status_code}"}
        except httpx.RequestError as e:
            return {"error": f"Request failed: {e}"}
        except ValueError:
            return {"error": "Invalid JSON response from cPanel API."}
        except Exception as e:
            return {"error": f"Unknown error occurred: {e}"}
