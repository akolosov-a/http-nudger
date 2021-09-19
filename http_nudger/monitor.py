import asyncio
import logging
import re
from pathlib import Path
from time import gmtime, perf_counter

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
    regexp: re.Pattern,
    kafka_bootstrap_servers: str,
    kafka_topic: str,
    kafka_key_file: Path,
    kafka_cert_file: Path,
    kafka_ca_file: Path,
):
    url_status_queue: asyncio.Queue = asyncio.Queue()
    kafka_producer = create_kafka_producer(
        kafka_bootstrap_servers,
        kafka_key_file,
        kafka_cert_file,
        kafka_ca_file,
    )
    await kafka_producer.start()

    checker_task = asyncio.create_task(
        url_status_checker(url, period, timeout, regexp, url_status_queue)
    )
    producer_task = asyncio.create_task(
        url_status_producer(kafka_producer, kafka_topic, url_status_queue)
    )

    try:
        await asyncio.gather(checker_task, producer_task)
    finally:
        await kafka_producer.stop()


async def url_status_checker(
    url: str, period: int, timeout: int, regexp: re.Pattern, queue: asyncio.Queue
):
    while True:
        logger.info("Checking URL %s...", url)
        url_status = url_check(url, timeout, regexp)
        logger.debug("URL status: %s", url_status)

        await queue.put(url_status)
        await asyncio.sleep(period)


def url_check(url: str, timeout: int, regexp: re.Pattern) -> UrlStatus:
    timestamp = gmtime()
    request_failure = None

    start_cnt = perf_counter()
    try:
        r = requests.get(url, timeout=timeout)
    except RequestException as ex:
        request_failure = ex
    exec_time = perf_counter() - start_cnt

    url_status = UrlStatus(
        timestamp,
        url,
        r.status_code,
        str(request_failure),
        exec_time,
        False,  # TODO: regex matching
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
