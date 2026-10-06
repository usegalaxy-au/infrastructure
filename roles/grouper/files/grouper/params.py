"""CLI argument parsing and runtime parameters."""
import argparse
from dataclasses import dataclass
from pathlib import Path

import config

# Parent of the `grouper` package: where approved_domains.json, users.json,
# config.py and .env live alongside it. Resolved once so importing this
# module from any working directory still finds them.
DEFAULT_GROUPER_DIR = Path(__file__).resolve().parent.parent

# Refuse to act on more than this many group membership changes in one run
# without --force - see build_arg_parser's --limit help text.
DEFAULT_CHANGE_LIMIT = 50


def build_arg_parser() -> argparse.ArgumentParser:
    """Build the grouper CLI argument parser."""
    parser = argparse.ArgumentParser(
        description='Manage user group memberships')
    parser.add_argument(
        '-c', '--commit', action='store_const', const=True, default=False,
        help="Act on the changes found. Without this flag, changes are "
             "listed but nothing is added, removed or notified for real")
    parser.add_argument(
        '-l', '--list', action='store_const', const=True, default=False,
        help="List domains currently associated with groups on Galaxy")
    parser.add_argument(
        '-n', '--notify', action='store_const', const=True, default=False,
        help="Notify in Slack of any new or removed Galaxy users")
    parser.add_argument(
        '-g', '--generate', action='store_true',
        help="Generate initial state of the users.json file")
    parser.add_argument(
        '--add', action='store_const', const=True, default=False,
        help="Add users automatically to groups based on email domains")
    parser.add_argument(
        '--remove', action='store_const', const=True, default=False,
        help="Remove users from groups they are not eligible for based on "
             "email domain")
    parser.add_argument(
        '--production', action='store_const', const=True, default=False,
        help="Act on the production server instead of the staging server "
             "by default")
    parser.add_argument(
        '--all', action='store_const', const=True, default=False,
        help="Check all Galaxy users, not just new ones")
    parser.add_argument(
        '--limit', type=int, default=DEFAULT_CHANGE_LIMIT,
        help="Refuse to add/remove more than this many group memberships "
             f"in one run without --force (default: {DEFAULT_CHANGE_LIMIT})")
    parser.add_argument(
        '--force', action='store_true',
        help="Act even if the number of changes exceeds --limit")
    parser.add_argument(
        '--grouper-dir', type=Path, default=None,
        help="Directory containing approved_domains.json and users.json, "
             "and where grouper.log is written (default: the directory "
             "containing this package)")
    return parser


@dataclass(frozen=True)
class Params:
    """Runtime parameters for a single grouper invocation."""

    galaxy_baseurl: str
    galaxy_api_key: str
    grouper_dir: Path
    dry_run: bool = True
    production: bool = False
    list_domains: bool = False
    add: bool = False
    remove: bool = False
    notify: bool = False
    all_users: bool = False
    generate: bool = False
    limit: int = DEFAULT_CHANGE_LIMIT
    force: bool = False

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> 'Params':
        """Resolve CLI args and config into a parameter set."""
        if args.production:
            galaxy_baseurl = config.PROD_GALAXY_BASEURL
            galaxy_api_key = config.PROD_GALAXY_API_KEY
        else:
            galaxy_baseurl = config.STAGING_GALAXY_BASEURL
            galaxy_api_key = config.STAGING_GALAXY_API_KEY

        return cls(
            galaxy_baseurl=galaxy_baseurl,
            galaxy_api_key=galaxy_api_key,
            grouper_dir=args.grouper_dir or DEFAULT_GROUPER_DIR,
            dry_run=not args.commit,
            production=args.production,
            list_domains=args.list,
            add=args.add,
            remove=args.remove,
            notify=args.notify,
            all_users=args.all,
            generate=args.generate,
            limit=args.limit,
            force=args.force,
        )
