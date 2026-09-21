"""Shared fixtures for the grouper test suite."""
import os
from pathlib import Path

import pytest

DATA_DIR = Path(__file__).resolve().parent / 'data'

# config.py reads these from the environment at import time. Set fakes
# before anything below imports (directly or transitively) the grouper
# package, so a dev machine or CI runner needs no real secrets to test.
os.environ.setdefault('STAGING_GALAXY_API_KEY', 'test-staging-key')
os.environ.setdefault('PROD_GALAXY_API_KEY', 'test-prod-key')
os.environ.setdefault('SLACK_TOKEN', 'test-slack-token')

from grouper.domains import DomainRules  # noqa: E402
from grouper.galaxy import Group, User  # noqa: E402
from grouper.grouper import Grouper  # noqa: E402
from grouper.params import Params  # noqa: E402
from grouper.state import UserStateStore  # noqa: E402


class FakeGalaxyClient:
    """Records add/remove calls; get_groups/get_users return canned data."""

    def __init__(self, groups: list = None, users: list = None):
        self.add_calls = []
        self.remove_calls = []
        self._groups = groups or []
        self._users = users or []

    def get_groups(self) -> list:
        """Return the canned groups this fake was built with."""
        return self._groups

    def get_users(self) -> list:
        """Return the canned users this fake was built with."""
        return self._users

    def add_user_to_group(self, user_id: str, group_id: str) -> bool:
        """Record the call and report success."""
        self.add_calls.append((user_id, group_id))
        return True

    def remove_user_from_group(self, user_id: str, group_id: str) -> bool:
        """Record the call and report success."""
        self.remove_calls.append((user_id, group_id))
        return True


class FakeSlackNotifier:
    """Records notify() calls instead of posting to Slack."""

    def __init__(self):
        self.notifications = []

    def notify(self, title: str, msg: str, colour: str) -> None:
        """Record the call instead of sending it."""
        self.notifications.append((title, msg, colour))


@pytest.fixture
def params(tmp_path):
    """A Params pointing grouper_dir at tmp_path, dry_run True by default."""
    return Params(
        galaxy_baseurl='https://example.invalid/api/',
        galaxy_api_key='test-key',
        grouper_dir=tmp_path,
        dry_run=True,
    )


@pytest.fixture
def fake_galaxy():
    """A GalaxyClient stand-in recording add/remove calls."""
    return FakeGalaxyClient()


@pytest.fixture
def make_galaxy():
    """Factory for a FakeGalaxyClient pre-loaded with groups/users."""
    def _make(groups=None, users=None):
        return FakeGalaxyClient(groups=groups, users=users)
    return _make


@pytest.fixture
def fake_slack():
    """A SlackNotifier stand-in recording (title, msg, colour) tuples."""
    return FakeSlackNotifier()


@pytest.fixture
def domains():
    """DomainRules loaded from the canned test approved_domains.json."""
    return DomainRules.from_file(DATA_DIR / 'approved_domains.json')


@pytest.fixture
def make_user():
    """Factory for a Galaxy User with only the fields tests care about."""
    def _make(id_, email=None):
        return User(id=id_, email=email)
    return _make


@pytest.fixture
def make_group():
    """Factory for a Galaxy Group with only the fields tests care about."""
    def _make(id_, name, users=None):
        return Group(id=id_, name=name, users=list(users or []))
    return _make


@pytest.fixture
def grouper(params, fake_galaxy, fake_slack, domains):
    """A Grouper wired up with fakes and a tmp_path-backed state store."""
    state = UserStateStore(params.grouper_dir / 'users.json')
    return Grouper(params, fake_galaxy, fake_slack, domains, state)
