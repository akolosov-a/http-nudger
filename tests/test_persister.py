from collections import namedtuple
from unittest.mock import AsyncMock, patch

import pytest

from http_nudger.persister import consume_batch


@pytest.mark.asyncio
@patch("aiokafka.AIOKafkaConsumer")
@patch("http_nudger.url_status.UrlStatus.from_json")
async def test_consume_batch(url_status_from_json_mock, aio_kafka_consumer_mock):
    ConsumerRecord = namedtuple("ConsumerRecord", ["value"])
    aio_kafka_consumer_mock.getmany = AsyncMock()
    aio_kafka_consumer_mock.getmany.return_value = {
        "topic1": [ConsumerRecord("msg1")],
        "topic2": [ConsumerRecord("msg2")],
        "topic3": [ConsumerRecord("msg3")],
    }
    url_status_from_json_mock.side_effect = ["something1", "something2", ValueError]

    batch = await consume_batch(aio_kafka_consumer_mock)
    assert len(batch) == 2
