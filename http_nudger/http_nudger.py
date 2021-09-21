import asyncio
import logging
import re

import click

from ._version import __version__
from .monitor import monitor_loop
from .persister import persister_loop

logger = logging.getLogger(__name__)


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.version_option(version=__version__)
def cli(debug):
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s;%(levelname)s;%(filename)s:%(lineno)s;%(message)s",
    )


def compile_regexp(ctx, param, value) -> re.Pattern:
    if not value:
        return None

    try:
        return re.compile(value)
    except re.error as ex:
        raise click.UsageError(f"Failed to parse given regexp: {ex}")


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
@click.option(
    "--regexp",
    callback=compile_regexp,
    help="Regular expression to search for in the response body",
)
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
def monitor(**kwargs):
    """Run monitoring for the specified URL"""
    asyncio.run(monitor_loop(**kwargs))


@cli.command()
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
@click.option(
    "--kafka-consumer-group",
    type=click.STRING,
    help="Kafka consumer group to join",
    default="http-nudger-url-statuses",
)
@click.option(
    "--postgres-host", type=click.STRING, help="Postgres hostname", default="localhost"
)
@click.option("--postgres-port", type=click.INT, help="Postgres port", default=5432)
@click.option(
    "--postgres-db",
    type=click.STRING,
    help="Postgres database",
    required=True,
)
@click.option(
    "--postgres-user",
    type=click.STRING,
    help="Postgres username",
    required=True,
)
@click.option(
    "--postgres-password",
    type=click.STRING,
    help="Postgres password",
    required=True,
)
def persister(**kwargs):
    """Run process for storing URL checks to the given database tables"""
    asyncio.run(persister_loop(**kwargs))
