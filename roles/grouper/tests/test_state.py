"""Tests for grouper.state.UserStateStore."""
import json

import pytest

from grouper.errors import GrouperUserError
from grouper.state import UserStateError, UserStateStore


def test_load_malformed_json_raises_user_error(tmp_path):
    path = tmp_path / 'users.json'
    path.write_text('["u1", "u2",]')  # trailing comma
    store = UserStateStore(path)

    with pytest.raises(UserStateError) as exc_info:
        store.load()

    assert str(path) in str(exc_info.value)


def test_user_state_error_is_a_grouper_user_error():
    """main() catches the base class, so the subclass must derive from it."""
    assert issubclass(UserStateError, GrouperUserError)


def test_load_missing_file_raises(tmp_path):
    """Current behaviour: no users.json is an unhandled FileNotFoundError.

    --generate is the documented workaround for a first run - see
    refactoring-plan.md Stage 2, "first run with no users.json".
    """
    store = UserStateStore(tmp_path / 'users.json')
    with pytest.raises(FileNotFoundError):
        store.load()


def test_save_then_load_round_trips(tmp_path):
    store = UserStateStore(tmp_path / 'users.json')
    store.save(['u2', 'u1'])
    assert store.load() == ['u1', 'u2']


def test_diff_no_change(tmp_path):
    store = UserStateStore(tmp_path / 'users.json')
    store.save(['u1', 'u2'])
    added, removed = store.diff(['u1', 'u2'])
    assert added == []
    assert removed == []


def test_diff_additions_only(tmp_path):
    store = UserStateStore(tmp_path / 'users.json')
    store.save(['u1'])
    added, removed = store.diff(['u1', 'u2'])
    assert added == ['u2']
    assert removed == []


def test_diff_removals_only(tmp_path):
    store = UserStateStore(tmp_path / 'users.json')
    store.save(['u1', 'u2'])
    added, removed = store.diff(['u1'])
    assert added == []
    assert removed == ['u2']


def test_diff_additions_and_removals(tmp_path):
    store = UserStateStore(tmp_path / 'users.json')
    store.save(['u1', 'u2'])
    added, removed = store.diff(['u2', 'u3'])
    assert added == ['u3']
    assert removed == ['u1']


def test_save_is_atomic_on_failure(tmp_path, monkeypatch):
    """A crash during the replace step must not touch the original file."""
    path = tmp_path / 'users.json'
    store = UserStateStore(path)
    store.save(['u1'])

    def raise_replace(src, dst):
        raise OSError('simulated crash mid-write')

    monkeypatch.setattr('grouper.state.os.replace', raise_replace)

    with pytest.raises(OSError):
        store.save(['u2'])

    with open(path) as f:
        assert json.load(f) == ['u1']
