"""Galaxy API client."""
import logging
import sys
from dataclasses import dataclass, field
from datetime import timedelta
from time import time
from typing import Optional

import requests

import config

REQUEST_TIMEOUT = 30  # seconds

logger = logging.getLogger(__name__)


class GalaxyAPIError(Exception):
    """Raised when the Galaxy API returns a non-200 response."""


@dataclass(frozen=True)
class User:
    """A Galaxy user."""

    id: str
    email: Optional[str] = None

    @classmethod
    def from_api(cls, data: dict) -> 'User':
        """Build a User from a Galaxy API user record."""
        return cls(id=data['id'], email=data.get('email'))


@dataclass(frozen=True)
class Group:
    """A Galaxy group, with its member users."""

    id: str
    name: str
    users: list = field(default_factory=list)

    @classmethod
    def from_api(cls, data: dict, users_data: list = None) -> 'Group':
        """Build a Group from a Galaxy API group record and its members."""
        users = [User.from_api(u) for u in (users_data or [])]
        return cls(id=data['id'], name=data['name'], users=users)


class GalaxyClient:
    """Owns the HTTP session, base URL and API key for one Galaxy server."""

    def __init__(
        self,
        baseurl: str,
        api_key: str,
        session: requests.Session = None,
    ):
        self._baseurl = baseurl
        self._session = session or requests.Session()
        self._session.headers.update({'x-api-key': api_key})

    def _get(self, path: str) -> requests.Response:
        """GET a path, raising GalaxyAPIError on a non-200 response."""
        res = self._session.get(
            self._baseurl + path, timeout=REQUEST_TIMEOUT)

        if res.status_code != 200:
            raise GalaxyAPIError(
                f"Request to {path} did not return ok: {res.reason}: "
                f"{res.text}")

        return res

    def get_groups(self) -> list:
        """Fetch all groups, each populated with its member users."""
        logger.info("Retrieving all groups")
        groups_data = self._get(config.GALAXY_GROUP_EP).json()
        logger.info("Found %d groups", len(groups_data))
        start = time()

        groups = []
        for i, group_data in enumerate(groups_data, start=1):
            if sys.stdout.isatty():
                sys.stdout.write(
                    f"Populating group: {group_data['name']} "
                    f"({i}/{len(groups_data)})   \r")
                sys.stdout.flush()

            users_data = self._get(
                config.GALAXY_GROUP_EP + group_data['id']
                + config.GALAXY_GROUP_USER_EP).json()
            groups.append(Group.from_api(group_data, users_data))

        logger.info(
            "%d groups queried. Total query time: %s",
            len(groups_data), timedelta(seconds=time() - start))
        return groups

    def get_users(self) -> list:
        """Fetch all Galaxy users."""
        start = time()
        users_data = self._get(config.GALAXY_USER_EP).json()
        users = [User.from_api(data) for data in users_data]

        logger.info(
            "%d users returned. Query took: %s",
            len(users), timedelta(seconds=time() - start))
        return users

    def add_user_to_group(self, user_id: str, group_id: str) -> bool:
        """Add a user to a group. Returns whether the API call succeeded."""
        path = config.GALAXY_GROUP_EP + group_id + "/users/" + user_id
        res = self._session.put(self._baseurl + path, timeout=REQUEST_TIMEOUT)
        return res.status_code == 200

    def remove_user_from_group(self, user_id: str, group_id: str) -> bool:
        """Remove a user from a group. Returns whether it succeeded."""
        path = config.GALAXY_GROUP_EP + group_id + "/users/" + user_id
        res = self._session.delete(
            self._baseurl + path, timeout=REQUEST_TIMEOUT)
        return res.status_code == 200
