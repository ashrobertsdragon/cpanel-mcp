"""Connector enum for CpanelEmail."""

from enum import Enum

from cpanel_mcp.connectors.cpanel_api import CpanelAPI
from cpanel_mcp.connectors.cpanel_ssh import CpanelSSH


class Connector(Enum):
    """Enum for supported cPanel connectors."""

    API = CpanelAPI
    SSH = CpanelSSH
