from unittest import mock

import pytest
from httpx import HTTPStatusError, Response

import server


class MockResponse(Response):
    """A minimal mock for httpx.Response."""

    def __init__(self, json_data=None, status_code=200):
        self._json_data = json_data if json_data is not None else {"ok": True}
        self.status_code = status_code

    def raise_for_status(self) -> "MockResponse":
        if self.status_code >= 400:
            raise HTTPStatusError(
                f"HTTP {self.status_code}", request=mock.Mock(), response=self
            )
        return self

    def json(self, **kwargs):
        return self._json_data


@pytest.fixture(autouse=True)
def env_vars(monkeypatch):
    """Sets up base environment variables for the API."""
    monkeypatch.setenv("USERNAME", "cpuser")
    monkeypatch.setenv("HOSTNAME", "cpanel.example.com")
    monkeypatch.setenv("CPANEL_API_TOKEN", "tok123")
    monkeypatch.delenv("PORT", raising=False)
    monkeypatch.delenv("SSL", raising=False)
    yield


@pytest.fixture
def mock_httpx_client():
    """Mocks the httpx.Client and yields the mock client instance."""
    with mock.patch.object(server.httpx, "Client") as m:
        client = mock.Mock()
        m.return_value = client
        yield client


@pytest.fixture(autouse=True)
def reset_cpanelapi_singleton():
    """Ensures CpanelAPI singleton is reset between tests."""
    server.CpanelAPI._singleton = None
    yield
    server.CpanelAPI._singleton = None


@pytest.fixture()
def cpanelapi_no_singleton():
    """Initializes a CpanelAPI instance."""
    return server.CpanelAPI()


@pytest.fixture
def expected_make_call_args():
    """Provides the expected base URL and headers for API calls."""
    return {
        "base_url": "https://cpanel.example.com:2083",
        "headers": {
            "Authorization": "cpanel cpuser:tok123",
            "Content-Type": "application/json",
        },
    }


@pytest.fixture
def make_mock_api_call_tester(mock_httpx_client):
    """
    A helper fixture to test API tool functions by setting a mock response
    and asserting the result and the mock client call arguments.
    """
    mock_httpx_client.get.return_value = MockResponse({"ok": 1})

    def _tester(
        func,
        *func_args,
        expected_module,
        expected_func,
        expected_params,
        **func_kwargs,
    ):
        res = func(*func_args, **func_kwargs)

        assert res == {"ok": 1}

        mock_httpx_client.get.assert_called_once()
        call_kwargs = mock_httpx_client.get.call_args.kwargs
        url = call_kwargs["url"]
        params = call_kwargs["params"]

        expected_url_end = f"/execute/{expected_module}/{expected_func}"
        assert url.endswith(expected_url_end)

        assert params == expected_params

        mock_httpx_client.get.reset_mock()

    return _tester


@pytest.fixture
def mock_response(*args, **kwargs):
    def _make_mock_response(*args, **kwargs):
        return MockResponse(*args, **kwargs)

    return _make_mock_response
