"""Abstract base class for cPanel connections."""

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import TypeAlias

Params: TypeAlias = Mapping[str, str | int]


class CpanelConnect(ABC):
    """Connect to cPanel account and make function calls."""

    @staticmethod
    def split_email(email: str) -> tuple[str, str]:
        """Split an email address into username and domain.

        Args:
            email (str): The email address to split.

        Returns:
            tuple[str, str]: A tuple containing the username and domain.
        """
        username = email.split("@")[0]
        domain = email.split("@")[1]

        return username, domain

    @abstractmethod
    def make_call(
        self,
        module: str,
        function: str,
        params: Params | None = None,
    ) -> dict[str, str]:
        """Make a call to the cPanel UAPI.

        Args:
            module (str): The cPanel UAPI module (e.g., "Email").
            function (str): The function to call (e.g., "add_pop").
            params (Params | None): The parameters to pass for the API call.

        Returns:
            dict[str, str]: The JSON response from the api.

        Raises:
            NotImplementedError: If the subclass does not implement this.
        """
        raise NotImplementedError
