"""
This module contains various helpers for communicating with Kafka
and PostgreSQL
"""
from pathlib import Path
from typing import Optional

import asyncpg
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.helpers import create_ssl_context


def create_kafka_producer(
    bootstrap_servers: str,
    key_file: Path,
    cert_file: Path,
    ca_file: Path,
) -> AIOKafkaProducer:
    ssl_context = create_ssl_context(
        certfile=cert_file, keyfile=key_file, cafile=ca_file
    )
    return AIOKafkaProducer(
        bootstrap_servers=bootstrap_servers,
        security_protocol="SSL",
        ssl_context=ssl_context,
    )


def create_kafka_consumer(
    bootstrap_servers: str,
    consumer_group: str,
    key_file: Path,
    cert_file: Path,
    ca_file: Path,
) -> AIOKafkaConsumer:
    ssl_context = create_ssl_context(
        certfile=cert_file, keyfile=key_file, cafile=ca_file
    )
    return AIOKafkaConsumer(
        bootstrap_servers=bootstrap_servers,
        security_protocol="SSL",
        ssl_context=ssl_context,
        enable_auto_commit=False,
        auto_offset_reset="earliest",
        group_id=consumer_group,
    )


async def create_postgres_connection_pool(
    host: str, port: int, db: str, user: str, password: str
) -> asyncpg.Pool:
    return await asyncpg.create_pool(
        user=user,
        password=password,
        database=db,
        host=host,
        port=port,
        min_size=1,
        max_size=1,
    )
