import sys

from mcp.server.fastmcp import FastMCP

from cpanel_mcp.connector import Connector
from cpanel_mcp.cpanel_email import CpanelEmail

"""MCP server entry point."""


def run_mcp(connector: Connector):
    """Run the MCP server with the specified connector.

    Args:
        connector (Connector): The connector to use.
    """
    mcp = FastMCP("cPanel Email Management")
    api = CpanelEmail(connector)
    for tool in api.tools():
        mcp.add_tool(tool)
    mcp.run()


def main() -> None:
    """Main entry point for the MCP server."""
    if len(sys.argv) < 2:
        raise ValueError("No connector specified")
    connector = sys.argv[1]
    if connector not in Connector.__members__:
        raise ValueError("Invalid connector specified")
    run_mcp(Connector[connector])


if __name__ == "__main__":
    main()
