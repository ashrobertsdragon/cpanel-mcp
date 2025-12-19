from unittest import mock
import inspect
import sys
import pytest
from cpanel_mcp.cli import main, create_parser


def test_create_parser():
    parser = create_parser()
    args = parser.parse_args(["api", "--add-email"])
    assert args.connector == "api"
    assert args.command == "add_email_account"


@pytest.mark.parametrize(
    "command_args, method_name, code_varnames, expected_call_kwargs",
    [
        (
            ["--add-email", "--email", "u@d.com", "--password", "pw"],
            "add_email_account",
            ("email", "password", "quota"),
            {"email": "u@d.com", "password": "pw"},
        ),
        (
            ["--delete-email", "--email", "u@d.com"],
            "delete_email_account",
            ("email",),
            {"email": "u@d.com"},
        ),
        (
            ["--list-accounts", "--domain", "d.com"],
            "list_email_accounts",
            ("domain",),
            {"domain": "d.com"},
        ),
        (
            ["--settings", "--email", "u@d.com"],
            "get_email_settings",
            ("email",),
            {"email": "u@d.com"},
        ),
        (
            ["--update-quota", "--email", "u@d.com", "--quota", "100"],
            "update_quota",
            ("email", "quota"),
            {"email": "u@d.com", "quota": "100"},
        ),
        (
            ["--change-password", "--email", "u@d.com", "--password", "newpw"],
            "change_password",
            ("email", "password"),
            {"email": "u@d.com", "password": "newpw"},
        ),
        (
            [
                "--create-forwarder",
                "--email",
                "u@d.com",
                "--destination",
                "dest@x.com",
            ],
            "create_email_forwarder",
            ("email", "destination"),
            {"email": "u@d.com", "destination": "dest@x.com"},
        ),
        (
            [
                "--delete-forwarder",
                "--email",
                "u@d.com",
                "--destination",
                "dest@x.com",
            ],
            "delete_email_forwarder",
            ("email", "destination"),
            {"email": "u@d.com", "destination": "dest@x.com"},
        ),
        (
            ["--list-forwarders", "--domain", "d.com"],
            "list_email_forwarders",
            ("domain",),
            {"domain": "d.com"},
        ),
    ],
)
def test_main_dispatch_commands(
    command_args, method_name, code_varnames, expected_call_kwargs
):
    """Parametrized test for all CLI commands."""
    test_args = ["cli.py", "api"] + command_args

    with mock.patch.object(sys, "argv", test_args):
        with mock.patch("cpanel_mcp.cli.CpanelEmail") as mock_email_cls:
            mock_api = mock_email_cls.return_value

            # Mock the method and its signature
            mock_method = mock.Mock()
            parameters = [
                inspect.Parameter(
                    name, inspect.Parameter.POSITIONAL_OR_KEYWORD
                )
                for name in code_varnames
            ]
            mock_method.__signature__ = inspect.Signature(parameters)

            setattr(mock_api, method_name, mock_method)

            main()

            mock_method.assert_called_once_with(**expected_call_kwargs)
