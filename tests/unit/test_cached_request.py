from unittest.mock import patch

import pytest

from rundeck_exporter.utils import _cache, _cache_lock, cached_request


class TestCachedRequest:
    def _clear(self, endpoint: str) -> None:
        with _cache_lock:
            _cache.pop(endpoint, None)

    @pytest.mark.parametrize("endpoint,return_value,expected_calls", [
        pytest.param("/cache/test/failure", None, 2, id="none-not-cached"),
        pytest.param("/cache/test/success", {"projects": []}, 1, id="payload-cached"),
    ])
    def test_caching_behavior(self, endpoint, return_value, expected_calls):
        """None results must not be cached (retried every call); successful results must be served from cache."""
        self._clear(endpoint)
        with patch("rundeck_exporter.utils.request", return_value=return_value) as mock_req:
            assert cached_request(endpoint) == return_value
            assert cached_request(endpoint) == return_value
        assert mock_req.call_count == expected_calls
