import os
import httpx
from mcp.shared.exceptions import MCPError
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel


mcp = FastMCP("cPanel Email Management")
API = None

class CpanelConfig(BaseModel):
    """Configuration for cPanel connection"""
    hostname: str
    username: str
    api_token: str
    port: int = 2083
    ssl: bool = True


class CpanelAPI:
    """Connects to the cPanel account via API token and makes function calls."""

    def __init__(self, config: CpanelConfig):
        self.config = config
        protocol = "https" if config.ssl else "http"
        self.base_url = f"{protocol}://{config.hostname}:{config.port}"
        self.client = httpx.AsyncClient(timeout=30.0)
        self.headers = {
            "Authorization": f"cpanel {self.config.username}:{self.config.api_token}",
            "Content-Type": "application/json",
        }
        
    def make_call(self, module: str, function: str, params: dict | None = None):
        """
        Makes a call to the cPanel UAPI using httpx.

        Args:
            module (str): The cPanel UAPI module (e.g., "Email").
            function (str): The function to call (e.g., "add_pop").
            params (dict): The parameters to pass for the API call.

        Returns:
            dict: The JSON response from the API.
        """
        if params is None:
            params = {}

        url = f"{self.base_url}/execute/{module}/{function}"
        
        try:
            response = httpx.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            return {"error": f"Request failed: {e}"}
        except ValueError:
            return {"error": "Invalid JSON response from cPanel API."}

    @staticmethod
    def split_email(email: str) -> tuple[str, str]"-:
        """Split an email address into username and domain"""
        username = email.split('@')[0]
        domain = email.split('@')[1]
        
        return username, domain

@mcp.tool
def add_email_account(email: str, password: str, quota: int = 0) -> dict:
    """Adds a new email account to the cPanel.

    Args:
        email (str): The full email address (e.g., "user@example.com").
        password (str): The password for the new email account.
        quota (int): The mailbox size limit in megabytes (MB) Default is 0 for unlimited.

    Returns:
        dict: The JSON response from the API.
    """
    check_API()
    username, domain = API.split_email(email)

    params = {
        "domain": domain,
        "email": username,
        "password": password,
        "quota": quota,
    }
    return API.make_call("Email", "add_pop", params)

@mcp.tool
def delete_email_account(email: str) -> dict:
    """Deletes an email account from the cPanel.

    Args:
        email (str): The full email address to delete (e.g., "user@example.com").

    Returns:
        dict: The JSON response from the API.
    """
    check_API()
    username, domain = API.split_email(email)

    params = {
        "domain": domain,
        "email": username,
    }
    return API.make_call("Email", "del_pop", params)

@mcp.tool
def list_email_accounts(domain: str) -> dict:
    """Lists all email accounts for a specific domain.

    Args:
        domain (str): The domain to list email accounts for (e.g., "example.com").

    Returns:
        dict: The JSON response from the API.
    """
    check_API()
    params = {
        "domain": domain,
    }
    return API.make_call("Email", "list_pops", params)

@mcp.tool
def get_email_settings(email: str) -> dict:
    """Retrieves the settings for a given email account.
    
    Args:
        email (str): The full email address for which to send client settings.
    
    Returns:
        dict: The JSON response from the API.
    """
    check_API()

    return API.make_call("Email", "get_client_settings")

@mcp.tool
def update_quota(email: str, quota: int) -> dict:
    """Changes the quota for a given email account.
    
    Args:
        email (str): The full email address for which to send client settings.
        quota (int): The new acount limit.
    
    Returns:
        dict: The JSON response from the API.
    """
    check_API()
    username, domain = API.split_email(email)
    
    params = {
        "username": username,
        "domain": domain,
        "quota": quota
    }

    return API.make_call("Email", "edit_pop_quota", params)

@mcp.tool
def change_password(email: str, new_password: str) -> dict:
    """Changes the password for a given email account.
    
    Args:
        email (str): The full email address for which to send client settings.
        new_password (str): The password to change to.
    
    Returns:
        dict: The JSON response from the API.
    """
    check_API()
    username, domain = API.split_email(email)

    params = {
        "username": username,
        "domain": domain,
        "password": new_password
    }

    return API.make_call("Email", "passwd_pop", params)

@mcp.tool
def create_email_forwarder(email: str, destination: str) -> dict:
    """Create an email forwarder.
    
    Args:
        email (str): The full email address for which to send client settings.
        destination (str): The full email address to forward email to.
    
    Returns:
        dict: The JSON response from the API.
    """
    check_API()
    username, domain = API.split_email(email)

    params = {
        "username": username,
        "domain": domain,
        "fwdopt": "fwd",
        "fwdemail": destination
    }

    return API.make_call("Email", "add_forwarder", params)
    
@mcp.tool
def delete_email_forwarder(email: str, destination: str) -> dict:
    """Delete an email forwarder.
    
    Args:
        email (str): The full email address for which to send client settings.
        destination (str): The full email address to foward email to.
    
    Returns:
        dict: The JSON response from the API.
    """
    check_API()

    params = {
        "address": email,
        "forwarder": destination
    }

    return API.make_call("Email", "delete_forwarder", params)
    
@mcp.tool
def list_email_forwarders(domain: str) -> dict:
    """List email forwarders.
    
    Args:
        domain (str): The domain to list email accounts for (e.g., "example.com").
    
    Returns:
        dict: The JSON response from the API.
    """
    check_API()

    params = {"domain": domain}
    
    return API.make_call("Email", "list_forwarders", params)
 
def check_api() -> CpanelAPI:
    if not API:
        main()
    
def main() -> None:
    global API

    username = os.environ.get("USERNAME")
    hostname = os.environ.get("HOSTNAME")
    api_token = os.environ.get("CPANEL_API_TOKEN")
    port = os.environ.get("PORT")
    ssl = os.environ.get("SSL", None)
    
    configs = {
        "hostname": hostname,
        "username": username,
        "api_token": api_token,
    }
    
    if port is not None:
        with contextlib.suppress(ValueError, TypeError):
            configs["port"] = int(port)
    
    if ssl is not None:
        if isinstance(ssl, str):
            config_kwargs["ssl"] = ssl.lower() in ("true", "1", "yes", "on")
        else:
            config_kwargs["ssl"] = bool(ssl)
    
    config = CpanelConfig(hostname, username, api_token, port, ssl)
    
    CpanelAPI(config)

if __name__ == "__main__":
    main()
