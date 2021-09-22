"""
Persister module contains part of the http-nudger which consumes
records from Kafka and stores them into the database
"""
import json
import logging
from pathlib import Path
from typing import List

import aiokafka
import asyncpg

from .helpers import create_kafka_consumer, create_postgres_connection_pool
from .url_status import UrlStatus

logger = logging.getLogger(__name__)


async def persister_loop(
    kafka_bootstrap_servers: str,
    kafka_topic: str,
    kafka_key: Path,
    kafka_cert: Path,
    kafka_ca: Path,
    kafka_consumer_group: str,
    postgres_host: str,
    postgres_port: int,
    postgres_db: str,
    postgres_user: str,
    postgres_password: str,
):
    kafka_consumer = create_kafka_consumer(
        kafka_bootstrap_servers,
        kafka_consumer_group,
        kafka_key,
        kafka_cert,
        kafka_ca,
    )
    pg_conn_pool = await create_postgres_connection_pool(
        postgres_host, postgres_port, postgres_db, postgres_user, postgres_password
    )
    async with kafka_consumer as kafka_consumer, pg_conn_pool.acquire() as pg_conn:
        kafka_consumer.subscribe(topics=[kafka_topic])
        while True:
            batch = await consume_batch(kafka_consumer)
            await store_batch(pg_conn, batch)
            await kafka_consumer.commit()


async def consume_batch(
    consumer: aiokafka.AIOKafkaConsumer, timeout: int = 10 * 1000
) -> List[UrlStatus]:
    records = await consumer.getmany(timeout_ms=timeout)
    batch = []
    for msgs in records.values():
        for msg in msgs:
            try:
                url_status = UrlStatus.from_json(msg.value)
                batch.append(url_status)
            except (TypeError, json.JSONDecodeError, ValueError):
                logger.warning("Skipping message due to wrong format: %s", msg)

    return batch


async def store_batch(connection: asyncpg.Connection, batch: List[UrlStatus]):
    print(batch)
