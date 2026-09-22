"""Logging configuration for the grouper CLI."""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'
MAX_LOG_BYTES = 1_000_000
LOG_BACKUP_COUNT = 5


def configure_logging(log_path: Path, level: int = logging.INFO) -> None:
    """Log to stdout and to a rotating file at `log_path`.

    `run_groups.sh` redirects stdout to a single `run_groups.log` that gets
    overwritten every cron tick, so the rotating file handler is what
    actually preserves history of past runs across restarts.
    """
    formatter = logging.Formatter(LOG_FORMAT)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        log_path, maxBytes=MAX_LOG_BYTES, backupCount=LOG_BACKUP_COUNT)
    file_handler.setFormatter(formatter)

    logging.basicConfig(
        level=level, handlers=[console_handler, file_handler], force=True)
