from collections.abc import Callable

from cpanel_mcp.connector import Connector
from cpanel_mcp.connectors.cpanel_connection import CpanelConnect, Params

"""Module for cPanel email management."""


class CpanelEmail:
    """Class to manage cPanel email accounts."""

    def __init__(self, connection: Connector) -> None:
        """Initialize CpanelEmail.

        Args:
            connection (Connector): The connector to use for the API.
        """
        _api = connection.value
        self._api: CpanelConnect = _api()

    @property
    def tools(self) -> list[Callable]:
        """Return a list of callable tools for this email manager.

        Returns:
            list[Callable]: List of tool functions.
        """
        return [
            self.add_email_account,
            self.delete_email_account,
            self.list_email_accounts,
            self.get_email_settings,
            self.update_quota,
            self.change_password,
            self.create_email_forwarder,
            self.delete_email_forwarder,
            self.list_email_forwarders,
        ]

    def add_email_account(
        self, email: str, password: str, quota: int = 0
    ) -> dict[str, str]:
        """Add a new email account.

        Args:
            email (str): The full email address (e.g., "user@example.com").
            password (str): The password for the new email account.
            quota (int): The mailbox size limit in megabytes (MB)
                Default is 0 for unlimited.

        Returns:
            dict[str, str]: The JSON response from the api.
        """
        username, domain = self._api.split_email(email)

        params: Params = {
            "domain": domain,
            "email": username,
            "password": password,
            "quota": quota,
        }
        return self._api.make_call("Email", "add_pop", params)

    def delete_email_account(self, email: str) -> dict[str, str]:
        """Delete an email account from domain.

        Args:
            email (str): The full email address to delete.
                (e.g., "user@example.com")

        Returns:
            dict[str, str]: The JSON response from the api.
        """
        username, domain = self._api.split_email(email)

        params: Params = {
            "domain": domain,
            "email": username,
        }
        return self._api.make_call("Email", "delete_pop", params)

    def list_email_accounts(self, domain: str) -> dict[str, str]:
        """Lists all email accounts for a specific domain.

        Args:
            domain (str): The domain for which to list email accounts.
                (e.g., "example.com")

        Returns:
            dict[str, str]: The JSON response from the api.
        """
        params: Params = {
            "domain": domain,
        }
        return self._api.make_call("Email", "list_pops", params)

    def get_email_settings(self, email: str) -> dict[str, str]:
        """Retrieves the settings for a given email account.

        Args:
            email (str): The full email address for which to send client
                settings.

        Returns:
            dict[str, str]: The JSON response from the api.
        """
        params: Params = {"email": email}

        return self._api.make_call("Email", "get_client_settings", params)

    def update_quota(self, email: str, quota: int) -> dict[str, str]:
        """Changes the quota for a given email account.

        Args:
            email (str): The full email address for which to send client
                settings.
            quota (int): The new acount limit.

        Returns:
            dict[str, str]: The JSON response from the api.
        """
        username, domain = self._api.split_email(email)

        params: Params = {"email": username, "domain": domain, "quota": quota}

        return self._api.make_call("Email", "edit_pop_quota", params)

    def change_password(self, email: str, password: str) -> dict[str, str]:
        """Changes the password for a given email account.

        Args:
            email (str): The full email address for which to send client
                settings.
            password (str): The password to change to.

        Returns:
            dict[str, str]: The JSON response from the api.
        """
        username, domain = self._api.split_email(email)

        params: Params = {
            "email": username,
            "domain": domain,
            "password": password,
        }

        return self._api.make_call("Email", "passwd_pop", params)

    def create_email_forwarder(
        self, email: str, destination: str
    ) -> dict[str, str]:
        """Create an email forwarder.

        Args:
            email (str): The full email address for which to send client
                settings.
            destination (str): The full email address to forward email to.

        Returns:
            dict[str, str]: The JSON response from the api.
        """
        username, domain = self._api.split_email(email)

        params: Params = {
            "email": username,
            "domain": domain,
            "fwdopt": "fwd",
            "fwdemail": destination,
        }

        return self._api.make_call("Email", "add_forwarder", params)

    def delete_email_forwarder(
        self, email: str, destination: str
    ) -> dict[str, str]:
        """Delete an email forwarder.

        Args:
            email (str): The full email address for which to send client
                settings.
            destination (str): The full email address to forward email to.

        Returns:
            dict[str, str]: The JSON response from the api.
        """
        params: Params = {"address": email, "forwarder": destination}

        return self._api.make_call("Email", "delete_forwarder", params)

    def list_email_forwarders(self, domain: str) -> dict[str, str]:
        """List email forwarders.

        Args:
            domain (str): The domain for which to list email accounts.
                (e.g., "example.com")

        Returns:
            dict[str, str]: The JSON response from the api.
        """
        params: Params = {"domain": domain}

        return self._api.make_call("Email", "list_forwarders", params)
