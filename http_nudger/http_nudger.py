import asyncio
import logging

import click

from ._version import __version__
from .monitor import monitor_loop

logger = logging.getLogger(__name__)


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.version_option(version=__version__)
def cli(debug):
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s;%(levelname)s;%(filename)s:%(lineno)s;%(message)s",
    )


@cli.command()
@click.argument("url", type=click.STRING, nargs=1)
@click.option(
    "--period",
    type=click.INT,
    default=30,
    show_default=True,
    help="How often to perform an HTTP request to the given URL (seconds)",
)
@click.option(
    "--timeout",
    type=click.INT,
    default=5,
    show_default=True,
    help="Timeout for an HTTP request (seconds)",
)
@click.option("--regexp", type=click.STRING, default="")
@click.option(
    "--kafka-bootstrap-servers",
    type=click.STRING,
    help="Kafka bootstrap servers list",
    required=True,
)
@click.option(
    "--kafka-topic",
    type=click.STRING,
    help="Kafka topic",
    required=True,
)
@click.option(
    "--kafka-key",
    type=click.Path(exists=True),
    help="Kafka access key file",
    required=True,
)
@click.option(
    "--kafka-cert",
    type=click.Path(exists=True),
    help="Kafka access certificate file",
    required=True,
)
@click.option(
    "--kafka-ca",
    type=click.Path(exists=True),
    help="Kafka root CA cert file",
    required=True,
)
# pylint: disable-msg=too-many-arguments
def monitor(
    url,
    period,
    timeout,
    regexp,
    kafka_bootstrap_servers,
    kafka_topic,
    kafka_key,
    kafka_cert,
    kafka_ca,
):
    """Run monitoring for the specified URL"""
    asyncio.run(
        monitor_loop(
            url,
            period,
            timeout,
            regexp,
            kafka_bootstrap_servers,
            kafka_topic,
            kafka_key,
            kafka_cert,
            kafka_ca,
        )
    )
