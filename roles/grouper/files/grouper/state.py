"""Persisted set of previously-seen Galaxy user ids."""
import json
import os
from pathlib import Path

from .errors import GrouperUserError


class UserStateError(GrouperUserError):
    """Raised when users.json exists but is not well-formed."""


class UserStateStore:
    """Owns users.json: the ids of users seen on a previous run."""

    def __init__(self, path: Path):
        self._path = path

    def load(self) -> list:
        """Return the user ids recorded on the previous run."""
        with open(self._path) as f:
            try:
                return json.load(f)
            except json.JSONDecodeError as e:
                raise UserStateError(
                    f"{self._path} is not valid JSON: {e}") from e

    def save(self, user_ids: list) -> None:
        """Atomically write the given user ids as the new state."""
        tmp_path = self._path.with_name(self._path.name + '.tmp')
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(sorted(user_ids), f, ensure_ascii=False, indent=4)
        os.replace(tmp_path, self._path)

    def diff(self, current_user_ids: list) -> tuple:
        """Return (added, removed) against the last-saved state."""
        past_user_ids = set(self.load())
        current_user_ids = set(current_user_ids)
        added = list(current_user_ids - past_user_ids)
        removed = list(past_user_ids - current_user_ids)
        return added, removed
