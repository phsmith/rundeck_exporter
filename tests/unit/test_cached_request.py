"""Tests for cached_request()'s TTL caching behavior."""

from unittest.mock import patch

import pytest

from rundeck_exporter.utils import _cache, _cache_lock, cached_request


class TestCachedRequest:
    """Verifies cache population, None-result bypass, and per-(endpoint, raw) key isolation."""

    def _clear(self, endpoint: str, raw: bool = False) -> None:
        """
        Remove the cached value for the specified endpoint/raw combination.
        """
        with _cache_lock:
            _cache.pop((endpoint, raw), None)

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

    def test_raw_and_parsed_results_cached_separately(self):
        """Calling the same endpoint with raw=False then raw=True must not reuse the other's cached value."""
        endpoint = "/cache/test/raw-vs-parsed"
        self._clear(endpoint, raw=False)
        self._clear(endpoint, raw=True)

        def _side_effect(_endpoint, raw=False):
            """Return a distinct value per raw flag, so a cache mix-up would be caught by the assertions."""
            return "raw text" if raw else {"parsed": True}

        with patch("rundeck_exporter.utils.request", side_effect=_side_effect) as mock_req:
            assert cached_request(endpoint) == {"parsed": True}
            assert cached_request(endpoint, raw=True) == "raw text"
            # Second round-trip must be served from cache, not re-fetched
            assert cached_request(endpoint) == {"parsed": True}
            assert cached_request(endpoint, raw=True) == "raw text"

        assert mock_req.call_count == 2
