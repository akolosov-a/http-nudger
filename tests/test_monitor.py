from http_nudger.monitor import url_check
from unittest.mock import patch
from time import gmtime
from requests import Response
from requests.exceptions import RequestException


def test_url_check():
    now = gmtime()
    url = "https://google.com"
    timeout = 5

    with patch("requests.get") as requests_get_mock, patch(
        "time.gmtime"
    ) as gmtime_mock:
        gmtime_mock.return_value = now

        resp = Response()
        resp.status_code = 200
        requests_get_mock.return_value = resp

        # Successful request
        url_status = url_check(url, timeout, None)
        assert url_status.timestamp == now
        assert url_status.url == url
        assert url_status.status_code == 200
        assert url_status.failure_reason == "None"

        # Failed request
        requests_get_mock.side_effect = RequestException("Some reason")
        url_status = url_check(url, timeout, None)
        assert url_status.timestamp == now
        assert url_status.url == url
        assert url_status.status_code == -1
        assert url_status.failure_reason == "Some reason"
