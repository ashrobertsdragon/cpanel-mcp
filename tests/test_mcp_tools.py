import pytest


def test_add_email_account_maps_params(make_mock_api_call_tester, cpanel_mcp):
    """Tests CpanelMCP.add_email_account parameter mapping to UAPI call."""
    make_mock_api_call_tester(
        cpanel_mcp.add_email_account,
        "u@d.com",
        "pw",
        quota=123,
        expected_module="Email",
        expected_func="add_pop",
        expected_params={
            "domain": "d.com",
            "email": "u",
            "password": "pw",
            "quota": 123,
        },
    )


def test_delete_email_account_maps_params(make_mock_api_call_tester, cpanel_mcp):
    """Tests CpanelMCP.delete_email_account parameter mapping to UAPI call."""
    make_mock_api_call_tester(
        cpanel_mcp.delete_email_account,
        "u@d.com",
        expected_module="Email",
        expected_func="delete_pop",
        expected_params={"domain": "d.com", "email": "u"},
    )


def test_list_email_accounts_maps_params(make_mock_api_call_tester, cpanel_mcp):
    """Tests CpanelMCP.list_email_accounts parameter mapping to UAPI call."""
    make_mock_api_call_tester(
        cpanel_mcp.list_email_accounts,
        "d.com",
        expected_module="Email",
        expected_func="list_pops",
        expected_params={"domain": "d.com"},
    )


def test_get_email_settings_maps_params(make_mock_api_call_tester, cpanel_mcp):
    """Tests CpanelMCP.get_email_settings parameter mapping to UAPI call."""
    make_mock_api_call_tester(
        cpanel_mcp.get_email_settings,
        "u@d.com",
        expected_module="Email",
        expected_func="get_client_settings",
        expected_params={"email": "u@d.com"},
    )


def test_update_quota_maps_params(make_mock_api_call_tester, cpanel_mcp):
    """Tests CpanelMCP.update_quota parameter mapping to UAPI call."""
    make_mock_api_call_tester(
        cpanel_mcp.update_quota,
        "u@d.com",
        10,
        expected_module="Email",
        expected_func="edit_pop_quota",
        expected_params={"email": "u", "domain": "d.com", "quota": 10},
    )


def test_change_password_maps_params(make_mock_api_call_tester, cpanel_mcp):
    """Tests CpanelMCP.change_password parameter mapping to UAPI call."""
    make_mock_api_call_tester(
        cpanel_mcp.change_password,
        "u@d.com",
        "new",
        expected_module="Email",
        expected_func="passwd_pop",
        expected_params={"email": "u", "domain": "d.com", "password": "new"},
    )


def test_create_email_forwarder_maps_params(make_mock_api_call_tester, cpanel_mcp):
    """Tests CpanelMCP.create_email_forwarder parameter mapping to UAPI call."""
    make_mock_api_call_tester(
        cpanel_mcp.create_email_forwarder,
        "u@d.com",
        "dest@x.com",
        expected_module="Email",
        expected_func="add_forwarder",
        expected_params={
            "email": "u",
            "domain": "d.com",
            "fwdopt": "fwd",
            "fwdemail": "dest@x.com",
        },
    )


def test_delete_email_forwarder_maps_params(make_mock_api_call_tester, cpanel_mcp):
    """Tests CpanelMCP.delete_email_forwarder parameter mapping to UAPI call."""
    make_mock_api_call_tester(
        cpanel_mcp.delete_email_forwarder,
        "u@d.com",
        "dest@x.com",
        expected_module="Email",
        expected_func="delete_forwarder",
        expected_params={"address": "u@d.com", "forwarder": "dest@x.com"},
    )


def test_list_email_forwarders_maps_params(make_mock_api_call_tester, cpanel_mcp):
    """Tests CpanelMCP.list_email_forwarders parameter mapping to UAPI call."""
    make_mock_api_call_tester(
        cpanel_mcp.list_email_forwarders,
        "d.com",
        expected_module="Email",
        expected_func="list_forwarders",
        expected_params={"domain": "d.com"},
    )
