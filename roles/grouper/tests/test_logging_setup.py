"""Tests for grouper.logging_setup."""
import logging

from grouper.logging_setup import (
    ANSI_RED,
    ANSI_RESET,
    LOG_FORMAT,
    ColourFormatter,
    configure_logging,
)


def make_record(level: int) -> logging.LogRecord:
    return logging.LogRecord(
        name='test', level=level, pathname=__file__, lineno=1,
        msg='something happened', args=(), exc_info=None)


def test_error_is_wrapped_in_red():
    formatted = ColourFormatter(LOG_FORMAT).format(
        make_record(logging.ERROR))

    assert formatted.startswith(ANSI_RED)
    assert formatted.endswith(ANSI_RESET)


def test_info_is_not_coloured():
    formatted = ColourFormatter(LOG_FORMAT).format(make_record(logging.INFO))

    assert ANSI_RED not in formatted


def test_no_escape_codes_reach_the_log_file(tmp_path, monkeypatch):
    """Under cron stdout is not a tty, so nothing should be colourised -
    and the file handler must never carry escape codes regardless.
    """
    monkeypatch.setattr('sys.stdout.isatty', lambda: False)
    log_path = tmp_path / 'grouper.log'
    configure_logging(log_path)

    logging.getLogger(__name__).error("a red herring")
    logging.shutdown()

    assert ANSI_RED not in log_path.read_text()
