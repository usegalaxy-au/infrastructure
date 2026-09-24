"""Expected, operator-fixable error conditions and how they're reported."""
import logging

logger = logging.getLogger(__name__)


class GrouperUserError(Exception):
    """Base for errors caused by bad input rather than a code fault.

    `__main__.main` catches these and hands them to `report_exception`,
    which reports a single ERROR line instead of a traceback: a malformed
    JSON file is something an operator fixes, not a crash to debug.
    Anything not deriving from this - a GalaxyAPIError, say - still
    tracebacks uncaught, which is the signal that something unexpected
    happened.
    """


def report_exception(exc: GrouperUserError) -> None:
    """Report an expected error as one ERROR line, with no traceback.

    Goes through `logging`, not `print`: `configure_logging` already
    attaches a stdout handler (red on a tty) and the rotating file
    handler, so a single call reaches the console and `grouper.log`
    without double-printing. The non-zero exit code that `main` returns
    alongside this is what triggers `run_groups.sh`'s Slack alert.
    """
    logger.error("%s", exc)
