import asyncio
import os
import random
import string
from unittest.mock import patch

import pytest
from requests import Response

from http_nudger.helpers import create_postgres_connection_pool
from http_nudger.monitor import monitor_loop
from http_nudger.persister import persister_loop

pytestmark = [pytest.mark.e2e]


@pytest.fixture
def http_response():
    resp = Response()
    resp.status_code = 200
    resp._content = b"ABC123"
    return resp


@pytest.mark.asyncio
@patch("requests.get")
async def test_check_to_db_flow(requests_get_mock, http_response):
    requests_get_mock.return_value = http_response

    pg_pool = await create_postgres_connection_pool(
        os.environ["PG_HOST"],
        os.environ["PG_PORT"],
        os.environ["PG_TEST_DB"],
        os.environ["PG_USER"],
        os.environ["PG_PASSWORD"],
    )
    async with pg_pool.acquire() as pg_conn:
        records = await pg_conn.execute("DROP TABLE IF EXISTS url_statuses")

    unique_url = "".join(random.choices(string.ascii_lowercase, k=10)) + ".com"

    monitor = monitor_loop(
        unique_url,
        10,
        5,
        None,
        os.environ["KAFKA_BOOTSTRAP_SERVERS"],
        os.environ["KAFKA_TEST_TOPIC"],
        "./kafka-key.pem",
        "./kafka-cert.pem",
        "./ca.pem",
    )

    persister = persister_loop(
        os.environ["KAFKA_BOOTSTRAP_SERVERS"],
        os.environ["KAFKA_TEST_TOPIC"],
        "./kafka-key.pem",
        "./kafka-cert.pem",
        "./ca.pem",
        "consumer-group",
        os.environ["PG_HOST"],
        os.environ["PG_PORT"],
        os.environ["PG_TEST_DB"],
        os.environ["PG_USER"],
        os.environ["PG_PASSWORD"],
    )

    try:
        await asyncio.wait_for(asyncio.gather(monitor, persister), timeout=15)
    except asyncio.TimeoutError:
        pass

    async with pg_pool.acquire() as pg_conn:
        records = await pg_conn.fetch(
            "SELECT * from url_statuses where url = $1", unique_url
        )
        assert len(records) > 0
