"""Tests for utils.request(): auth routing, error handling, endpoint prefixing, and raw responses."""

from unittest.mock import MagicMock, patch

import httpx
import pytest
from prometheus_client import REGISTRY

from rundeck_exporter import utils
from rundeck_exporter.utils import request


def _api_error_count(endpoint: str) -> float:
    """
    Retrieve the error count for an endpoint from the Prometheus registry.
    
    Returns:
    	float: The error count, or 0.0 if the sample is not present.
    """
    return REGISTRY.get_sample_value("rundeck_exporter_api_errors_total", {"endpoint": endpoint}) or 0.0


def _make_ok_response(payload) -> MagicMock:
    """
    Create a mock HTTP response that simulates a successful request.
    
    Parameters:
        payload: The JSON payload to return when the mock's `json()` method is called.
    
    Returns:
        A MagicMock configured with `raise_for_status()` returning None and `json()` returning the given payload.
    """
    mock = MagicMock()
    mock.raise_for_status.return_value = None
    mock.json.return_value = payload
    return mock


def _make_status_error_response(status_code: int) -> MagicMock:
    """
    Create a mock response that raises an HTTP status error when raise_for_status() is called.
    
    Parameters:
        status_code (int): The HTTP status code for the error response.
    
    Returns:
        MagicMock: A mock response object configured to raise httpx.HTTPStatusError with the given status code when raise_for_status() is invoked.
    """
    error_response = MagicMock(status_code=status_code, text="Error")
    mock = MagicMock()
    mock.raise_for_status.side_effect = httpx.HTTPStatusError(
        str(status_code), request=MagicMock(), response=error_response
    )
    return mock


class TestRequest:
    """Verifies error handling, auth-mode routing, endpoint prefixing, and raw vs. JSON responses."""

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
        """Any transport error, timeout, or API-level error flag must return None and bump the error counter."""
        endpoint = f"/test/{endpoint_suffix}"
        before = _api_error_count(endpoint)

        with patch.object(utils._token_client, "get", **mock_kwargs):
            assert request(endpoint) is None

        assert _api_error_count(endpoint) == before + 1

    def test_successful_request_returns_json(self):
        """A successful response must be returned as parsed JSON."""
        endpoint = "/test/success"
        payload = [{"id": 1, "name": "proj"}]

        with patch.object(utils._token_client, "get", return_value=_make_ok_response(payload)):
            assert request(endpoint) == payload

    def test_error_counter_uses_normalized_endpoint_label(self):
        """The error counter's endpoint label must strip query params and generalize the project name."""
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
            """
            Simulate a successful login response.
            
            Returns:
                MagicMock: A mock response object.
            """
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

    def test_token_auth_skips_api_prefix_for_prometheus_endpoint(self):
        """Token auth must not prepend /api/{version} to Rundeck 6's native Prometheus endpoint —
        it lives outside the versioned API namespace, same as session auth."""
        endpoint = "/monitoring/prometheus"
        payload = {"ok": True}

        with patch.object(utils._token_client, "get", return_value=_make_ok_response(payload)) as mock_get:
            assert request(endpoint) == payload

        called_url = mock_get.call_args.args[0]
        assert called_url == f"{utils.args.rundeck_url}{endpoint}"
        assert "/api/" not in called_url

    def test_token_auth_keeps_api_prefix_for_legacy_metrics_endpoint(self):
        """Unlike /monitoring/prometheus, the legacy /metrics/metrics endpoint rejects token auth
        when called without the /api/{version} prefix (redirects to the login page), so token auth
        must keep using the prefixed form — only session auth gets the unprefixed path."""
        endpoint = "/metrics/metrics"
        payload = {"ok": True}

        with patch.object(utils._token_client, "get", return_value=_make_ok_response(payload)) as mock_get:
            assert request(endpoint) == payload

        called_url = mock_get.call_args.args[0]
        assert called_url == f"{utils.args.rundeck_url}/api/{utils.args.rundeck_api_version}{endpoint}"

    def test_user_password_auth_skips_api_prefix_for_legacy_metrics_endpoint(self):
        """Session auth keeps the pre-existing no-prefix behavior for /metrics/metrics."""
        endpoint = "/metrics/metrics"
        payload = {"ok": True}

        with patch.object(utils, "RUNDECK_USERPASSWORD", "secret"):
            with patch.object(utils.args, "rundeck_username", "admin"):
                utils._user_client.cookies.set("JSESSIONID", "fake-session")
                try:
                    with patch.object(utils._user_client, "get", return_value=_make_ok_response(payload)) as mock_get:
                        assert request(endpoint) == payload
                finally:
                    utils._user_client.cookies.clear()

        called_url = mock_get.call_args.args[0]
        assert called_url == f"{utils.args.rundeck_url}{endpoint}"
        assert "/api/" not in called_url

    def test_raw_returns_response_text_without_json_parsing(self):
        """request(endpoint, raw=True) must return response.text and never call response.json()."""
        endpoint = "/monitoring/prometheus"
        mock = MagicMock()
        mock.raise_for_status.return_value = None
        mock.text = "# HELP some_metric \nsome_metric 1.0\n"

        with patch.object(utils._token_client, "get", return_value=mock):
            result = request(endpoint, raw=True)

        assert result == mock.text
        mock.json.assert_not_called()

    def test_session_cookie_cleared_on_401(self):
        """A 401 response from the user client must clear the JSESSIONID so the next call re-authenticates."""
        endpoint = "/system/info"

        with patch.object(utils, "RUNDECK_USERPASSWORD", "secret"):
            with patch.object(utils.args, "rundeck_username", "admin"):
                utils._user_client.cookies.set("JSESSIONID", "expired-session")
                with patch.object(utils._user_client, "get", return_value=_make_status_error_response(401)):
                    request(endpoint)
                assert not utils._user_client.cookies.get("JSESSIONID")
