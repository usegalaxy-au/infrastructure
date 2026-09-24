"""Logging configuration for the grouper CLI."""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'
MAX_LOG_BYTES = 1_000_000
LOG_BACKUP_COUNT = 5

ANSI_RED = '\033[31m'
ANSI_RESET = '\033[0m'


class ColourFormatter(logging.Formatter):
    """Renders ERROR and above in red.

    Only ever attached to the console handler, and only when stdout is a
    tty: under cron `run_groups.sh` redirects stdout to a file, and the
    rotating file handler writes `grouper.log`, so escape codes must not
    reach either.
    """

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)

        if record.levelno >= logging.ERROR:
            return f"{ANSI_RED}{message}{ANSI_RESET}"

        return message


def configure_logging(log_path: Path, level: int = logging.INFO) -> None:
    """Log to stdout and to a rotating file at `log_path`.

    `run_groups.sh` redirects stdout to a single `run_groups.log` that gets
    overwritten every cron tick, so the rotating file handler is what
    actually preserves history of past runs across restarts.
    """
    formatter = logging.Formatter(LOG_FORMAT)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(
        ColourFormatter(LOG_FORMAT) if sys.stdout.isatty() else formatter)

    file_handler = RotatingFileHandler(
        log_path, maxBytes=MAX_LOG_BYTES, backupCount=LOG_BACKUP_COUNT)
    file_handler.setFormatter(formatter)

    logging.basicConfig(
        level=level, handlers=[console_handler, file_handler], force=True)
