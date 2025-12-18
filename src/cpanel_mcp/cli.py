import argparse

from cpanel_mcp.connector import Connector
from cpanel_mcp.cpanel_email import CpanelEmail

"""CLI entry point."""


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI.

    Returns:
        argparse.ArgumentParser: The populated argument parser.
    """
    parser = argparse.ArgumentParser(
        "cPanel mail tools", description="CLI for cPanel-MCP"
    )
    parser.add_argument(
        "connector", help="Connector to use", choices=["api", "ssh"]
    )
    parser.add_argument("--domain", help="Domain name")
    parser.add_argument("--email", help="Email address")
    parser.add_argument("--password", help="Email password")
    parser.add_argument("--quota", help="Email quota")

    command = parser.add_mutually_exclusive_group(required=True)
    command.add_argument(
        "-a",
        "--add-email",
        action="store_const",
        const="add_email_account",
        dest="command",
    )
    command.add_argument(
        "-d",
        "--delete-email",
        action="store_const",
        const="delete_email_account",
        dest="command",
    )
    command.add_argument(
        "-l",
        "--list-accounts",
        action="store_const",
        const="list_email_accounts",
        dest="command",
    )
    command.add_argument(
        "-s",
        "--settings",
        action="store_const",
        const="get_email_settings",
        dest="command",
    )
    command.add_argument(
        "-u",
        "--update-quota",
        action="store_const",
        const="update_quota",
        dest="command",
    )
    command.add_argument(
        "-p",
        "--change-password",
        action="store_const",
        const="change_password",
        dest="command",
    )
    command.add_argument(
        "-f",
        "--create-forwarder",
        action="store_const",
        const="create_email_forwarder",
        dest="command",
    )
    command.add_argument(
        "-r",
        "--delete-forwarder",
        action="store_const",
        const="delete_email_forwarder",
    )
    command.add_argument(
        "--list-forwarders",
        action="store_const",
        const="list_email_forwarders",
        dest="command",
    )

    return parser


def main() -> None:
    """Run the CLI application."""
    args = create_parser().parse_args()
    connector = Connector[args.connector.upper()]
    api = CpanelEmail(connector)

    tool = getattr(api, args.command)

    kwargs = {
        name: getattr(args, name)
        for name in tool.__code__.co_varnames
        if hasattr(args, name)
    }

    tool(**kwargs)
