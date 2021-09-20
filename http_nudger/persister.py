import logging
from pathlib import Path

from .helpers import create_kafka_consumer, create_postgres_connection
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

    pg_con = await create_postgres_connection(
        postgres_host, postgres_port, postgres_db, postgres_user, postgres_password
    )

    try:
        await kafka_consumer.start()
        kafka_consumer.subscribe(topics=[kafka_topic])
        async for msg in kafka_consumer:
            print(
                "{}:{:d}:{:d}: key={} value={} timestamp_ms={}".format(
                    msg.topic,
                    msg.partition,
                    msg.offset,
                    msg.key,
                    msg.value,
                    msg.timestamp,
                )
            )
            # logger.debug(
            #     "%s:%d:%d: key=%s value=%s timestamp_ms=%s",
            #     msg.topic,
            #     msg.partition,
            #     msg.offset,
            #     msg.key,
            #     msg.value,
            #     msg.timestamp,
            # )
            url_status = UrlStatus.from_json(msg.value)
            print(url_status)

    finally:
        kafka_consumer.unsubscribe()
        await kafka_consumer.stop()
