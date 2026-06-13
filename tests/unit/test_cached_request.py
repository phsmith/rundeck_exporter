from unittest.mock import patch

from rundeck_exporter.utils import _cache, _cache_lock, cached_request


class TestCachedRequest:
    def _clear(self, endpoint: str) -> None:
        with _cache_lock:
            _cache.pop(endpoint, None)

    def test_does_not_cache_none(self):
        """A failed request (None) must not be cached; it must be retried on every call."""
        endpoint = "/cache/failure/unique-a"
        self._clear(endpoint)

        with patch("rundeck_exporter.utils.request", return_value=None) as mock_req:
            assert cached_request(endpoint) is None
            assert cached_request(endpoint) is None

        assert mock_req.call_count == 2, "Failed requests must not be cached"

    def test_caches_successful_result(self):
        """A successful request must be cached; the second call must not hit the network."""
        endpoint = "/cache/success/unique-b"
        self._clear(endpoint)

        payload = {"projects": []}
        with patch("rundeck_exporter.utils.request", return_value=payload) as mock_req:
            assert cached_request(endpoint) == payload
            assert cached_request(endpoint) == payload

        assert mock_req.call_count == 1, "Successful results must be served from cache on second call"
