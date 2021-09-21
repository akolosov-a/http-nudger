import asyncio
import logging
import re
from pathlib import Path
from time import gmtime, perf_counter
from typing import Optional

import requests
from aiokafka import AIOKafkaProducer
from requests.exceptions import RequestException

from .helpers import create_kafka_producer
from .url_status import UrlStatus

logger = logging.getLogger(__name__)


# pylint: disable-msg=too-many-arguments
async def monitor_loop(
    url: str,
    period: int,
    timeout: int,
    regexp: Optional[re.Pattern],
    kafka_bootstrap_servers: str,
    kafka_topic: str,
    kafka_key: Path,
    kafka_cert: Path,
    kafka_ca: Path,
):
    url_status_queue: asyncio.Queue = asyncio.Queue()
    async with create_kafka_producer(
        kafka_bootstrap_servers,
        kafka_key,
        kafka_cert,
        kafka_ca,
    ) as kafka_producer:
        checker_task = asyncio.create_task(
            url_status_checker(url, period, timeout, regexp, url_status_queue)
        )
        producer_task = asyncio.create_task(
            url_status_producer(kafka_producer, kafka_topic, url_status_queue)
        )
        await asyncio.gather(checker_task, producer_task)


async def url_status_checker(
    url: str,
    period: int,
    timeout: int,
    regexp: Optional[re.Pattern],
    queue: asyncio.Queue,
):
    while True:
        logger.info("Checking URL %s...", url)
        url_status = url_check(url, timeout, regexp)
        logger.debug("URL status: %s", url_status)

        await queue.put(url_status)
        await asyncio.sleep(period)


def url_check(url: str, timeout: int, regexp: Optional[re.Pattern]) -> UrlStatus:
    timestamp = gmtime()
    resp = None
    request_failure = None
    regexp_str = regexp.pattern if regexp else None
    regexp_matched = False
    start_cnt = perf_counter()
    try:
        resp = requests.get(url, timeout=timeout)
        if regexp:
            regexp_matched = bool(regexp.search(resp.text))
    except RequestException as ex:
        request_failure = str(ex)
    exec_time = perf_counter() - start_cnt

    url_status = UrlStatus(
        timestamp,
        url,
        resp.status_code if resp else -1,
        request_failure,
        exec_time,
        regexp_str,
        regexp_matched,
    )

    return url_status


async def url_status_producer(
    producer: AIOKafkaProducer, topic: str, queue: asyncio.Queue
):
    while True:
        url_status = await queue.get()
        logger.debug("Starting processing URL status: %s", url_status)

        await producer.send(topic, url_status.to_json().encode())

        queue.task_done()
