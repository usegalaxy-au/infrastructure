"""Tests for CLI parsing (grouper.params) and the entrypoint."""
import pytest

import config
from grouper.params import Params, build_arg_parser


def test_flags_land_on_params_fields():
    parser = build_arg_parser()
    args = parser.parse_args([
        '--commit', '--list', '--notify', '--add', '--remove', '--all',
    ])

    params = Params.from_args(args)

    assert params.dry_run is False
    assert params.list_domains is True
    assert params.notify is True
    assert params.add is True
    assert params.remove is True
    assert params.all_users is True
    assert params.generate is False
    assert params.production is False


def test_generate_flag():
    parser = build_arg_parser()
    args = parser.parse_args(['--generate'])

    assert Params.from_args(args).generate is True


def test_production_selects_prod_server():
    parser = build_arg_parser()
    args = parser.parse_args(['--production'])

    params = Params.from_args(args)

    assert params.production is True
    assert params.galaxy_baseurl == config.PROD_GALAXY_BASEURL
    assert params.galaxy_api_key == config.PROD_GALAXY_API_KEY


def test_default_selects_staging_server():
    parser = build_arg_parser()
    args = parser.parse_args([])

    params = Params.from_args(args)

    assert params.production is False
    assert params.galaxy_baseurl == config.STAGING_GALAXY_BASEURL
    assert params.galaxy_api_key == config.STAGING_GALAXY_API_KEY


def test_dry_run_default_is_true():
    """Stage 3 bug 5 (fixed): --dryrun was replaced with an explicit
    --commit flag, so `groups.py --add` with no other flags now lists
    changes without acting on them.
    """
    parser = build_arg_parser()
    args = parser.parse_args([])

    assert Params.from_args(args).dry_run is True


def test_commit_flag_disables_dry_run():
    parser = build_arg_parser()
    args = parser.parse_args(['--commit'])

    assert Params.from_args(args).dry_run is False


def test_galaxy_api_error_propagates_from_main(monkeypatch):
    """A GalaxyAPIError isn't caught anywhere, so it tracebacks out of
    main() uncaught - which is what gives run_groups.sh a non-zero exit
    code via the interpreter's own crash handling.
    """
    from grouper import __main__ as entrypoint
    from grouper.galaxy import GalaxyAPIError

    class BoomGalaxyClient:
        def __init__(self, *args, **kwargs):
            pass

        def get_users(self):
            raise GalaxyAPIError('boom')

    monkeypatch.setattr(entrypoint, 'GalaxyClient', BoomGalaxyClient)

    with pytest.raises(GalaxyAPIError):
        entrypoint.main([])
