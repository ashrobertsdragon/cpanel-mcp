from unittest import mock

import httpx
import pytest

from server import CpanelAPI


@pytest.mark.parametrize(
    "port, ssl, expected_url",
    [
        # Defaults
        (None, None, "https://cpanel.example.com:2083"),
        # Override port, default ssl
        ("2087", "true", "https://cpanel.example.com:2087"),
        # Override both
        ("2082", "false", "http://cpanel.example.com:2082"),
        # Default port, override ssl
        (None, "false", "http://cpanel.example.com:2083"),
    ],
)
def test_build_config_variants(monkeypatch, port, ssl, expected_url):
    """Tests CpanelAPI construction with various PORT and SSL settings."""
    if port is not None:
        monkeypatch.setenv("PORT", port)
    else:
        monkeypatch.delenv("PORT", raising=False)

    if ssl is not None:
        monkeypatch.setenv("SSL", ssl)
    else:
        monkeypatch.delenv("SSL", raising=False)

    api = CpanelAPI()

    assert api._base_url == expected_url


def test_headers_include_cpanel_auth(
    cpanelapi_no_singleton, expected_make_call_args
):
    """Tests that the API client includes the required headers."""
    api = cpanelapi_no_singleton
    assert api._headers == expected_make_call_args["headers"]


def test_make_call_success(
    mock_httpx_client,
    mock_response,
    cpanelapi_no_singleton,
):
    """Tests a successful make_call."""
    mock_httpx_client.get.return_value = mock_response({"result": "ok"})
    module = "Email"
    func = "add_pop"
    params_in = {"email": "user", "domain": "ex.com"}
    api = cpanelapi_no_singleton

    response = api.make_call(module, func, params_in)

    assert response == {"result": "ok"}

    mock_httpx_client.get.assert_called_once()


def test_make_call_builds_url_and_params(
    mock_httpx_client,
    mock_response,
    cpanelapi_no_singleton,
    expected_make_call_args,
):
    """Verifies the client call arguments"""
    mock_httpx_client.get.return_value = mock_response({"result": "ok"})
    module = "Email"
    func = "add_pop"
    params_in = {"email": "user", "domain": "ex.com"}
    api = cpanelapi_no_singleton

    api.make_call(module, func, params_in)

    call_kwargs = mock_httpx_client.get.call_args.kwargs

    expected_url = (
        f"{expected_make_call_args['base_url']}/execute/{module}/{func}"
    )

    assert call_kwargs["url"] == expected_url
    assert call_kwargs["headers"] == expected_make_call_args["headers"]
    assert call_kwargs["params"] == params_in


def test_make_call_handles_request_error(
    mock_httpx_client, cpanelapi_no_singleton
):
    """Tests error handling for httpx.RequestError (e.g., network failure)."""
    mock_httpx_client.get.side_effect = httpx.RequestError(
        "Network is unreachable"
    )
    api = cpanelapi_no_singleton

    response = api.make_call("Email", "x")

    assert response == {"error": "Request failed: Network is unreachable"}


def test_make_call_handles_invalid_json(
    mock_httpx_client, cpanelapi_no_singleton, mock_response
):
    """Tests error handling when the response cannot be parsed as JSON."""
    bad_response = mock_response()

    def bad_json():
        raise ValueError("Non-JSON data received")

    bad_response.json = bad_json
    mock_httpx_client.get.return_value = bad_response
    api = cpanelapi_no_singleton

    response = api.make_call("Email", "x")
    assert response == {"error": "Invalid JSON response from cPanel API."}


def test_make_call_handles_http_error(
    mock_httpx_client, cpanelapi_no_singleton, mock_response
):
    """Tests error handling for HTTP status codes >= 400."""
    mock_httpx_client.get.return_value = mock_response(status_code=500)
    api = cpanelapi_no_singleton

    response = api.make_call("Email", "x")

    assert response == {"error": "HTTP 500"}


def test_split_email():
    """Tests the static method for splitting email addresses."""
    user, domain = CpanelAPI.split_email("name@domain.com")
    assert user == "name"
    assert domain == "domain.com"


def test_split_email_with_subdomain():
    user, domain = CpanelAPI.split_email("user.alias@sub.domain.co.uk")
    assert user == "user.alias"
    assert domain == "sub.domain.co.uk"
