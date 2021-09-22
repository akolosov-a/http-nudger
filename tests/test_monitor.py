import re
from datetime import datetime
from unittest.mock import patch

import pytest
from requests import Response
from requests.exceptions import RequestException

from http_nudger.monitor import url_check

URL = "https://google.com"


@pytest.fixture
def http_response():
    resp = Response()
    resp.status_code = 200
    resp._content = b"ABC123"
    return resp


@patch("requests.get")
def test_url_check(requests_get_mock, freezer, http_response):
    now = datetime.utcnow()

    requests_get_mock.return_value = http_response
    url_status = url_check(URL, 5, None)
    assert url_status.timestamp == now
    assert url_status.url == URL
    assert url_status.status_code == http_response.status_code
    assert url_status.failure_reason is None
    assert url_status.regexp is None
    assert url_status.regexp_matched is False

    requests_get_mock.side_effect = RequestException("Some reason")
    url_status = url_check(URL, 5, None)
    assert url_status.timestamp == now
    assert url_status.url == URL
    assert url_status.status_code == -1
    assert url_status.failure_reason == "Some reason"
    assert url_status.regexp is None
    assert url_status.regexp_matched is False


@patch("requests.get")
def test_url_check_regexp_match(requests_get_mock, http_response):
    regexp = re.compile("[0-9]+")

    requests_get_mock.return_value = http_response
    url_status = url_check(URL, 5, regexp)
    assert url_status.regexp == regexp.pattern
    assert url_status.regexp_matched is True

    requests_get_mock.side_effect = RequestException("Some reason")
    url_status = url_check(URL, 5, regexp)
    assert url_status.regexp == regexp.pattern
    assert url_status.regexp_matched is False


@patch("requests.get")
def test_url_check_regexp_not_match(requests_get_mock, http_response):
    regexp = re.compile("DEF?")

    requests_get_mock.return_value = http_response
    url_status = url_check(URL, 5, regexp)
    assert url_status.regexp == regexp.pattern
    assert url_status.regexp_matched is False

    requests_get_mock.side_effect = RequestException("Some reason")
    url_status = url_check(URL, 5, regexp)
    assert url_status.regexp == regexp.pattern
    assert url_status.regexp_matched is False
