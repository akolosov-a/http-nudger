from pathlib import Path

from aiokafka import AIOKafkaProducer
from aiokafka.helpers import create_ssl_context


def create_kafka_producer(
    kafka_bootstrap_servers: str,
    kafka_key_file: Path,
    kafka_cert_file: Path,
    kafka_ca_file: Path,
) -> AIOKafkaProducer:
    ssl_context = create_ssl_context(
        certfile=kafka_cert_file, keyfile=kafka_key_file, cafile=kafka_ca_file
    )
    return AIOKafkaProducer(
        bootstrap_servers=kafka_bootstrap_servers,
        security_protocol="SSL",
        ssl_context=ssl_context,
    )
