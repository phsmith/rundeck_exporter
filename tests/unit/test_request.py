from unittest.mock import MagicMock, patch

import httpx
import pytest
from prometheus_client import REGISTRY

from rundeck_exporter import utils
from rundeck_exporter.utils import request


def _api_error_count(endpoint: str) -> float:
    return REGISTRY.get_sample_value("rundeck_exporter_api_errors_total", {"endpoint": endpoint}) or 0.0


def _make_ok_response(payload) -> MagicMock:
    mock = MagicMock()
    mock.raise_for_status.return_value = None
    mock.json.return_value = payload
    return mock


def _make_status_error_response(status_code: int) -> MagicMock:
    error_response = MagicMock(status_code=status_code, text="Error")
    mock = MagicMock()
    mock.raise_for_status.side_effect = httpx.HTTPStatusError(
        str(status_code), request=MagicMock(), response=error_response
    )
    return mock


class TestRequest:
    @pytest.mark.parametrize("mock_kwargs,endpoint_suffix", [
        pytest.param(
            {"return_value": _make_status_error_response(500)},
            "http_status_error",
            id="http-status-error",
        ),
        pytest.param(
            {"side_effect": httpx.TimeoutException("timed out")},
            "timeout",
            id="timeout",
        ),
        pytest.param(
            {"side_effect": httpx.ConnectError("refused")},
            "conn_error",
            id="connect-error",
        ),
        pytest.param(
            {"return_value": _make_ok_response({"error": True, "message": "Not authorized"})},
            "api_error_flag",
            id="api-error-flag",
        ),
    ])
    def test_error_returns_none_and_increments_counter(self, mock_kwargs, endpoint_suffix):
        endpoint = f"/test/{endpoint_suffix}"
        before = _api_error_count(endpoint)

        with patch.object(utils._token_client, "get", **mock_kwargs):
            assert request(endpoint) is None

        assert _api_error_count(endpoint) == before + 1

    def test_successful_request_returns_json(self):
        endpoint = "/test/success"
        payload = [{"id": 1, "name": "proj"}]

        with patch.object(utils._token_client, "get", return_value=_make_ok_response(payload)):
            assert request(endpoint) == payload

    def test_error_counter_uses_normalized_endpoint_label(self):
        endpoint = "/project/MyProject/executions?max=20"
        normalized = "/project/{project}/executions"
        before = _api_error_count(normalized)

        with patch.object(utils._token_client, "get", side_effect=httpx.ConnectError("refused")):
            assert request(endpoint) is None

        assert _api_error_count(normalized) == before + 1

    def test_user_password_auth_routes_to_user_client(self):
        """When username+password are configured, all endpoints must use _user_client, not _token_client."""
        endpoint = "/system/info"
        payload = {"system": {}}

        with patch.object(utils, "RUNDECK_USERPASSWORD", "secret"):
            with patch.object(utils.args, "rundeck_username", "admin"):
                utils._user_client.cookies.set("JSESSIONID", "fake-session")
                try:
                    with patch.object(utils._user_client, "get", return_value=_make_ok_response(payload)) as mock_user:
                        with patch.object(utils._token_client, "get") as mock_token:
                            result = request(endpoint)
                finally:
                    utils._user_client.cookies.clear()

        assert result == payload
        mock_user.assert_called_once()
        mock_token.assert_not_called()

    def test_user_password_auth_authenticates_only_once_across_calls(self):
        """j_security_check must be posted at most once even when request() is called multiple times."""
        endpoint = "/system/info"
        payload = {"system": {}}

        def _login(*_args, **_kwargs):
            utils._user_client.cookies.set("JSESSIONID", "fake-session")
            return MagicMock()

        with patch.object(utils, "RUNDECK_USERPASSWORD", "secret"):
            with patch.object(utils.args, "rundeck_username", "admin"):
                utils._user_client.cookies.clear()
                with patch.object(utils._user_client, "post", side_effect=_login) as mock_post:
                    with patch.object(utils._user_client, "get", return_value=_make_ok_response(payload)):
                        request(endpoint)
                        request(endpoint)
                utils._user_client.cookies.clear()

        mock_post.assert_called_once()

    def test_session_cookie_cleared_on_401(self):
        """A 401 response from the user client must clear the JSESSIONID so the next call re-authenticates."""
        endpoint = "/system/info"

        with patch.object(utils, "RUNDECK_USERPASSWORD", "secret"):
            with patch.object(utils.args, "rundeck_username", "admin"):
                utils._user_client.cookies.set("JSESSIONID", "expired-session")
                with patch.object(utils._user_client, "get", return_value=_make_status_error_response(401)):
                    request(endpoint)
                assert not utils._user_client.cookies.get("JSESSIONID")
