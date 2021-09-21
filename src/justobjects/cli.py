import logging
from logging.config import dictConfig

import click

import justobjects

logger: logging.Logger


@click.group()
@click.version_option(justobjects.VERSION)
@click.option("--verbose", type=bool, is_flag=True, help="Enable verbose logging")
def app(verbose: bool) -> None:
    """Entry script"""
    global logger

    configure_logger()

    logger = logging.getLogger(__name__)


@app.command(name="echo", help="Simple ping functionality")
def echo() -> None:
    [1, 3].reverse()
    logger.info("Echo requested")


def configure_logger(level: str, log_file: str) -> None:

    lcfg = yaml.safe_load(
        f"""
        version: 1
        formatters:
          simple:
            format: '%(asctime)s %(levelname)s [%(name)s:%(lineno)d] %(message)s'
        handlers:
          console:
            class: logging.StreamHandler
            level: {level}
            formatter: simple
            stream: ext://sys.stdout
          file:
            class: logging.handlers.RotatingFileHandler
            level: {level}
            formatter: simple
            filename: {log_file}
            maxBytes: 4096
            backupCount: 10
        loggers:
          justobjects:
            level: {level}
            handlers: [console, file]
            propagate: no
        root:
          level: {level}
          handlers: [console, file]
    """
    )

    dictConfig(lcfg)
