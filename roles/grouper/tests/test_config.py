"""Tests for grouper.config.check_required_vars.

config.py itself is imported once per process (conftest.py sets fake env
vars before that first import - see its comment), so these tests exercise
check_required_vars() directly against a monkeypatched environment rather
than reloading the module.
"""
import pytest

import config
from grouper.errors import GrouperUserError


def test_check_required_vars_passes_when_all_set():
    config.check_required_vars()  # conftest.py has set fakes for all of them


def test_check_required_vars_raises_when_a_var_is_missing(monkeypatch):
    monkeypatch.delenv('SLACK_TOKEN', raising=False)

    with pytest.raises(config.ConfigError, match='SLACK_TOKEN'):
        config.check_required_vars()


def test_check_required_vars_reports_every_missing_var(monkeypatch):
    monkeypatch.delenv('STAGING_GALAXY_API_KEY', raising=False)
    monkeypatch.delenv('PROD_GALAXY_BASEURL', raising=False)

    with pytest.raises(config.ConfigError) as exc_info:
        config.check_required_vars()

    assert 'STAGING_GALAXY_API_KEY' in str(exc_info.value)
    assert 'PROD_GALAXY_BASEURL' in str(exc_info.value)


def test_check_required_vars_treats_empty_string_as_set(monkeypatch):
    """SLACK_ALERT_MENTIONS/SLACK_LOG_MENTIONS are legitimately '' when
    there's nobody to @mention - that must not count as missing.
    """
    monkeypatch.setenv('SLACK_ALERT_MENTIONS', '')

    config.check_required_vars()


def test_config_error_is_a_grouper_user_error():
    """main() catches the base class, so the subclass must derive from it."""
    assert issubclass(config.ConfigError, GrouperUserError)
