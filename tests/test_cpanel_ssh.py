from unittest import mock
import pytest
from cpanel_mcp.connectors.cpanel_ssh import CpanelSSH


@pytest.fixture
def ssh_env_vars(monkeypatch):
    monkeypatch.setenv("SSH_KEY_PATH", "/path/to/key")
    monkeypatch.setenv("SERVER_IP", "1.2.3.4")
    monkeypatch.setenv("CPANEL_USERNAME", "cpuser")
    monkeypatch.setenv("SSH_PORT", "2222")


def test_make_call_success(ssh_env_vars):
    with mock.patch("subprocess.run") as mock_run:
        mock_process = mock.Mock()
        mock_process.returncode = 0
        mock_process.stdout = "output"
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        ssh = CpanelSSH()
        assert ssh._config.ssh_port == 2222

        res = ssh.make_call("Module", "func", {"param": "val"})

        assert res == {"response": "output"}

        mock_run.assert_called_once()
        args = mock_run.call_args.args[0]
        assert "ssh" in args
        assert "-p" in args
        assert "2222" in args
        assert "cpuser@1.2.3.4" in args
        assert "/path/to/key" in args
        cmd = args[-1]
        assert "uapi Module func" in cmd
        assert "{'param': 'val'}" in cmd


def test_make_call_failure(ssh_env_vars):
    with mock.patch("subprocess.run") as mock_run:
        mock_process = mock.Mock()
        mock_process.returncode = 1
        mock_process.stdout = ""
        mock_process.stderr = "Error message"
        mock_run.return_value = mock_process

        ssh = CpanelSSH()
        res = ssh.make_call("Module", "func")

        assert res == {"stderror": "Error message"}
