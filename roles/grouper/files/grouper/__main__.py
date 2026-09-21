"""Entrypoint: build Params from argv, run a pass, set the exit code."""
import sys

import config

from .domains import DomainRules
from .galaxy import GalaxyClient
from .grouper import Grouper
from .params import Params, build_arg_parser
from .slack_notify import SlackNotifier
from .state import UserStateStore

APPROVED_DOMAINS_FILENAME = 'approved_domains.json'
USERS_FILENAME = 'users.json'


def main(argv: list = None) -> int:
    """Parse argv, wire up collaborators and run a grouper pass."""
    args = build_arg_parser().parse_args(argv)
    params = Params.from_args(args)

    galaxy = GalaxyClient(params.galaxy_baseurl, params.galaxy_api_key)
    slack = SlackNotifier(config.SLACK_TOKEN, dry_run=params.dry_run)
    domains = DomainRules.from_file(
        params.grouper_dir / APPROVED_DOMAINS_FILENAME)
    state = UserStateStore(params.grouper_dir / USERS_FILENAME)

    grouper = Grouper(params, galaxy, slack, domains, state)
    grouper.main()
    return 0


if __name__ == '__main__':
    sys.exit(main())
