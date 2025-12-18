from unittest import mock
import pytest
import sys
from cpanel_mcp.server import main
from cpanel_mcp.connector import Connector


def test_main_no_args():
    with mock.patch.object(sys, "argv", ["server.py"]):
        with pytest.raises(ValueError, match="No connector specified"):
            main()


def test_main_invalid_connector():
    with mock.patch.object(sys, "argv", ["server.py", "INVALID"]):
        with pytest.raises((ValueError, KeyError)):
            main()


def test_main_valid_connector():
    with mock.patch.object(sys, "argv", ["server.py", "API"]):
        with mock.patch("cpanel_mcp.server.run_mcp") as mock_run:
            main()
            mock_run.assert_called_once_with(Connector.API)
