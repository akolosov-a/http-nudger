from http_nudger.monitor import url_check
from unittest.mock import patch
from time import gmtime
from requests import Response

def test_url_check():
    now = gmtime()
    url = 'https://google.com'
    timeout = 5

    with patch("requests.get") as requests_get_mock, patch(
        "time.perf_counter"
    ) as perf_counter_mock, patch("time.gmtime") as gmtime_mock:
        gmtime_mock.return_value = now
        perf_counter_mock.side_effect = [1.0, 2.0]

        resp = Response()
        resp.status_code = 200
        requests_get_mock.return_value = resp

        url_status = url_check(url, timeout, None)
        assert url_status.timestamp == now
        assert url_status.url == url
        assert url_status.status_code == 200
        assert url_status.failure_reason == 'None'
