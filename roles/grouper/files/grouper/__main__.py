"""Entrypoint: build Params from argv, run a pass, set the exit code."""
import sys

import config

from .domains import DomainRules
from .galaxy import GalaxyClient
from .grouper import Grouper
from .logging_setup import configure_logging
from .params import Params, build_arg_parser
from .slack_notify import SlackNotifier
from .state import UserStateStore

APPROVED_DOMAINS_FILENAME = 'approved_domains.json'
USERS_FILENAME = 'users.json'
LOG_FILENAME = 'grouper.log'


def main(argv: list = None) -> int:
    """Parse argv, wire up collaborators and run a grouper pass.

    Returns 0 on success, 1 on a handled failure (e.g. Galaxy returned no
    users, or the change-limit safety valve refused to act). Unhandled
    exceptions - e.g. a GalaxyAPIError from a failed request - traceback
    uncaught, which is what gives run_groups.sh a non-zero exit code via
    the interpreter's own crash handling.
    """
    args = build_arg_parser().parse_args(argv)
    params = Params.from_args(args)
    configure_logging(params.grouper_dir / LOG_FILENAME)

    galaxy = GalaxyClient(params.galaxy_baseurl, params.galaxy_api_key)
    slack = SlackNotifier(config.SLACK_TOKEN, dry_run=params.dry_run)
    domains = DomainRules.from_file(
        params.grouper_dir / APPROVED_DOMAINS_FILENAME)
    state = UserStateStore(params.grouper_dir / USERS_FILENAME)

    grouper = Grouper(params, galaxy, slack, domains, state)
    return 0 if grouper.main() else 1


if __name__ == '__main__':
    sys.exit(main())
