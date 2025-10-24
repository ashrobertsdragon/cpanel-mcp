import contextlib
import os
from collections.abc import Mapping
from typing import Any, Self, TypeAlias

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ValidationError

Params: TypeAlias = Mapping[str, str | int]


class CpanelConfig(BaseModel):
    """Configuration for cPanel connection"""

    hostname: str
    username: str
    api_token: str
    port: int = 2083
    ssl: bool = True


class CpanelAPI:
    """Connects to the cPanel account via API token & makes function calls."""

    _singleton: Self | None = None

    def __new__(cls) -> Self:
        if not cls._singleton:
            cls._singleton = super().__new__(cls)
        return cls._singleton

    def __init__(self):
        self._config = self._build_config()
        protocol = "https" if self._config.ssl else "http"
        self._base_url = (
            f"{protocol}://{self._config.hostname}:{self._config.port}"
        )
        self._client = httpx.Client(timeout=30.0)
        self._headers = {
            "Authorization": (
                f"cpanel {self._config.username}:{self._config.api_token}"
            ),
            "Content-Type": "application/json",
        }

    @staticmethod
    def _build_config() -> CpanelConfig:
        username = os.environ["USERNAME"]
        hostname = os.environ["HOSTNAME"]
        api_token = os.environ["CPANEL_API_TOKEN"]

        port_ = os.environ.get("PORT")
        use_ssl = os.environ.get("SSL", None)

        configs: dict[str, Any] = {
            "hostname": hostname,
            "username": username,
            "api_token": api_token,
        }

        if port_ is not None:
            with contextlib.suppress(ValueError, TypeError):
                configs["port"] = int(port_)

        if use_ssl is not None:
            if isinstance(use_ssl, str):
                configs["ssl"] = use_ssl.lower() in ("true", "1", "yes", "on")
            else:
                configs["ssl"] = bool(use_ssl)
        try:
            return CpanelConfig(**configs)
        except ValidationError as e:
            errors = e.errors(include_input=True, include_context=True)
            error_message = (
                f"{e.error_count()} number of configuration inputs were "
                "incorrect:\n" + "\n".join([str(error) for error in errors])
            )
            raise RuntimeError(error_message) from e

    def make_call(
        self,
        module: str,
        function: str,
        params: Params | None = None,
    ) -> dict[str, str]:
        """
        Makes a call to the cPanel UAPI using httpx.

        Args:
            module (str): The cPanel UAPI module (e.g., "Email").
            function (str): The function to call (e.g., "add_pop").
            params (dict[str, str]): The parameters to pass for the API call.

        Returns:
            dict: The JSON response from the api.
        """
        if params is None:
            params = {}

        url = f"{self._base_url}/execute/{module}/{function}"

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

    @staticmethod
    def split_email(email: str) -> tuple[str, str]:
        """Split an email address into username and domain"""
        username = email.split("@")[0]
        domain = email.split("@")[1]

        return username, domain


class CpanelMCP:
    mcp = FastMCP("cPanel Email Management")

    def __init__(self) -> None:
        self._api = CpanelAPI()

    @mcp.tool()
    def add_email_account(
        self, email: str, password: str, quota: int = 0
    ) -> dict[str, str]:
        """Adds a new email account to the cPanel.

        Args:
            email (str): The full email address (e.g., "user@example.com").
            password (str): The password for the new email account.
            quota (int): The mailbox size limit in megabytes (MB)
                Default is 0 for unlimited.

        Returns:
            dict: The JSON response from the api.
        """
        username, domain = self._api.split_email(email)

        params: Params = {
            "domain": domain,
            "email": username,
            "password": password,
            "quota": quota,
        }
        return self._api.make_call("Email", "add_pop", params)

    @mcp.tool()
    def delete_email_account(self, email: str) -> dict[str, str]:
        """Deletes an email account from the cPanel.

        Args:
            email (str): The full email address to delete.
                (e.g., "user@example.com")

        Returns:
            dict: The JSON response from the api.
        """
        username, domain = self._api.split_email(email)

        params: Params = {
            "domain": domain,
            "email": username,
        }
        return self._api.make_call("Email", "delete_pop", params)

    @mcp.tool()
    def list_email_accounts(self, domain: str) -> dict[str, str]:
        """Lists all email accounts for a specific domain.

        Args:
            domain (str): The domain for which to list email accounts.
                (e.g., "example.com")

        Returns:
            dict: The JSON response from the api.
        """
        params: Params = {
            "domain": domain,
        }
        return self._api.make_call("Email", "list_pops", params)

    @mcp.tool()
    def get_email_settings(self, email: str) -> dict[str, str]:
        """Retrieves the settings for a given email account.

        Args:
            email (str): The full email address for which to send client settings.

        Returns:
            dict: The JSON response from the api.
        """
        params: Params = {"email": email}

        return self._api.make_call("Email", "get_client_settings", params)

    @mcp.tool()
    def update_quota(self, email: str, quota: int) -> dict[str, str]:
        """Changes the quota for a given email account.

        Args:
            email (str): The full email address for which to send client settings.
            quota (int): The new acount limit.

        Returns:
            dict: The JSON response from the api.
        """
        username, domain = self._api.split_email(email)

        params: Params = {"email": username, "domain": domain, "quota": quota}

        return self._api.make_call("Email", "edit_pop_quota", params)

    @mcp.tool()
    def change_password(self, email: str, new_password: str) -> dict[str, str]:
        """Changes the password for a given email account.

        Args:
            email (str): The full email address for which to send client settings.
            new_password (str): The password to change to.

        Returns:
            dict: The JSON response from the api.
        """
        username, domain = self._api.split_email(email)

        params: Params = {
            "email": username,
            "domain": domain,
            "password": new_password,
        }

        return self._api.make_call("Email", "passwd_pop", params)

    @mcp.tool()
    def create_email_forwarder(
        self, email: str, destination: str
    ) -> dict[str, str]:
        """Create an email forwarder.

        Args:
            email (str): The full email address for which to send client settings.
            destination (str): The full email address to forward email to.

        Returns:
            dict: The JSON response from the api.
        """
        username, domain = self._api.split_email(email)

        params: Params = {
            "email": username,
            "domain": domain,
            "fwdopt": "fwd",
            "fwdemail": destination,
        }

        return self._api.make_call("Email", "add_forwarder", params)

    @mcp.tool()
    def delete_email_forwarder(
        self, email: str, destination: str
    ) -> dict[str, str]:
        """Delete an email forwarder.

        Args:
            email (str): The full email address for which to send client settings.
            destination (str): The full email address to forward email to.

        Returns:
            dict: The JSON response from the api.
        """
        params: Params = {"address": email, "forwarder": destination}

        return self._api.make_call("Email", "delete_forwarder", params)

    @mcp.tool()
    def list_email_forwarders(self, domain: str) -> dict[str, str]:
        """List email forwarders.

        Args:
            domain (str): The domain for which to list email accounts.
                (e.g., "example.com")

        Returns:
            dict: The JSON response from the api.
        """
        params: Params = {"domain": domain}

        return self._api.make_call("Email", "list_forwarders", params)


def main() -> None:
    CpanelMCP()


if __name__ == "__main__":
    main()
