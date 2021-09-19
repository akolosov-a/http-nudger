import logging
from pathlib import Path

from .helpers import create_kafka_consumer

logger = logging.getLogger(__name__)


async def persister_loop(
    kafka_bootstrap_servers: str,
    kafka_topic: str,
    kafka_key: Path,
    kafka_cert: Path,
    kafka_ca: Path,
    postgres_host: str,
    postgres_port: int,
    postgres_key: Path,
    postgres_cert: Path,
    postgres_ca: Path,
):
    kafka_consumer = create_kafka_consumer(
        kafka_bootstrap_servers,
        kafka_topic,
        kafka_key,
        kafka_cert,
        kafka_ca,
    )

    await kafka_consumer.start()
    try:
        async for msg in kafka_consumer:
            print(
                "{}:{:d}:{:d}: key={} value={} timestamp_ms={}".format(
                    msg.topic, msg.partition, msg.offset, msg.key, msg.value,
                    msg.timestamp)
            )
    finally:
        await kafka_consumer.stop()
