from time import gmtime

from http_nudger.url_status import UrlStatus


def test_url_status():
    timestamp = gmtime()

    status1 = UrlStatus(timestamp, "https://google.com", 200, "", 0.5, False)
    status1_json = status1.to_json()

    status2 = UrlStatus.from_json(status1_json)

    assert status1 == status2
