from unittest import mock
import sys
from cpanel_mcp.cli import main, create_parser


def test_create_parser():
    parser = create_parser()
    args = parser.parse_args(["api", "--add-email"])
    assert args.connector == "api"
    assert args.command == "add_email_account"


def test_main_dispatch():
    # Test dispatching to add_email_account
    test_args = [
        "cli.py",
        "api",
        "--add-email",
        "--email",
        "u@d.com",
        "--password",
        "pw",
    ]
    with mock.patch.object(sys, "argv", test_args):
        with mock.patch("cpanel_mcp.cli.CpanelEmail") as mock_email_cls:
            mock_api = mock_email_cls.return_value
            mock_api.add_email_account = mock.Mock()
            mock_api.add_email_account.__code__ = mock.Mock()
            mock_api.add_email_account.__code__.co_varnames = (
                "email",
                "password",
                "quota",
            )

            main()

            mock_api.add_email_account.assert_called_once_with(
                email="u@d.com", password="pw", quota=None
            )


def test_main_dispatch_list_accounts():
    test_args = [
        "cli.py",
        "ssh",
        "--list-accounts",
        "--domain",
        "example.com",
    ]
    with mock.patch.object(sys, "argv", test_args):
        with mock.patch("cpanel_mcp.cli.CpanelEmail") as mock_email_cls:
            mock_api = mock_email_cls.return_value
            mock_api.list_email_accounts = mock.Mock()
            mock_api.list_email_accounts.__code__ = mock.Mock()
            mock_api.list_email_accounts.__code__.co_varnames = ("domain",)

            main()

            mock_api.list_email_accounts.assert_called_once_with(
                domain="example.com"
            )
