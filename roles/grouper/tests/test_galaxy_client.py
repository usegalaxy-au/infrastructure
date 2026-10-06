"""Tests for grouper.galaxy.GalaxyClient, against the `responses` library."""
import json
from pathlib import Path
from unittest.mock import patch

import pytest
import responses

import config
from grouper.galaxy import REQUEST_TIMEOUT, GalaxyAPIError, GalaxyClient

DATA_DIR = Path(__file__).resolve().parent / 'data'
BASEURL = 'https://example.invalid/api/'


def load(name):
    with open(DATA_DIR / name) as f:
        return json.load(f)


@responses.activate
def test_get_groups_populates_members():
    groups_data = load('groups.json')
    members_data = load('group_users.json')

    responses.add(
        responses.GET, BASEURL + config.GALAXY_GROUP_EP,
        json=groups_data, status=200)
    for group in groups_data:
        responses.add(
            responses.GET,
            BASEURL + config.GALAXY_GROUP_EP + group['id']
            + config.GALAXY_GROUP_USER_EP,
            json=members_data, status=200)

    client = GalaxyClient(BASEURL, 'secret-key')
    groups = client.get_groups()

    assert [g.name for g in groups] == ['AU Researchers', 'Staff']
    assert all(len(g.users) == 2 for g in groups)
    assert groups[0].users[0].email == 'alice@uq.edu.au'


@responses.activate
def test_get_groups_raises_on_non_200_group_list():
    responses.add(
        responses.GET, BASEURL + config.GALAXY_GROUP_EP,
        json={'err': 'nope'}, status=500)

    client = GalaxyClient(BASEURL, 'secret-key')
    with pytest.raises(GalaxyAPIError):
        client.get_groups()


@responses.activate
def test_get_groups_raises_on_non_200_group_members():
    groups_data = load('groups.json')
    responses.add(
        responses.GET, BASEURL + config.GALAXY_GROUP_EP,
        json=groups_data, status=200)
    responses.add(
        responses.GET,
        BASEURL + config.GALAXY_GROUP_EP + groups_data[0]['id']
        + config.GALAXY_GROUP_USER_EP,
        json={}, status=500)

    client = GalaxyClient(BASEURL, 'secret-key')
    with pytest.raises(GalaxyAPIError):
        client.get_groups()


@responses.activate
def test_get_users_returns_users():
    users_data = load('users.json')
    responses.add(
        responses.GET, BASEURL + config.GALAXY_USER_EP,
        json=users_data, status=200)

    client = GalaxyClient(BASEURL, 'secret-key')
    users = client.get_users()

    assert [u.id for u in users] == ['u1', 'u2', 'u3']


@responses.activate
def test_get_users_raises_on_non_200():
    responses.add(
        responses.GET, BASEURL + config.GALAXY_USER_EP,
        body='<html>internal error</html>', status=500)

    client = GalaxyClient(BASEURL, 'secret-key')
    with pytest.raises(GalaxyAPIError):
        client.get_users()


@responses.activate
def test_api_key_travels_in_header_not_url():
    responses.add(
        responses.GET, BASEURL + config.GALAXY_GROUP_EP,
        json=[], status=200)

    client = GalaxyClient(BASEURL, 'super-secret-key')
    client.get_groups()

    assert len(responses.calls) == 1
    req = responses.calls[0].request
    assert req.headers['x-api-key'] == 'super-secret-key'
    assert 'super-secret-key' not in req.url


@responses.activate
def test_timeout_passed_on_every_request():
    responses.add(
        responses.GET, BASEURL + config.GALAXY_USER_EP,
        json=[], status=200)

    client = GalaxyClient(BASEURL, 'secret-key')
    with patch.object(
        client._session, 'get', wraps=client._session.get,
    ) as spy:
        client.get_users()

    spy.assert_called_once()
    assert spy.call_args.kwargs['timeout'] == REQUEST_TIMEOUT


@responses.activate
def test_add_user_to_group_success():
    responses.add(
        responses.PUT,
        BASEURL + config.GALAXY_GROUP_EP + 'g1/users/u1',
        status=200)

    client = GalaxyClient(BASEURL, 'secret-key')
    assert client.add_user_to_group('u1', 'g1') is True


@responses.activate
def test_add_user_to_group_failure():
    responses.add(
        responses.PUT,
        BASEURL + config.GALAXY_GROUP_EP + 'g1/users/u1',
        status=500)

    client = GalaxyClient(BASEURL, 'secret-key')
    assert client.add_user_to_group('u1', 'g1') is False


@responses.activate
def test_remove_user_from_group_success():
    responses.add(
        responses.DELETE,
        BASEURL + config.GALAXY_GROUP_EP + 'g1/users/u1',
        status=200)

    client = GalaxyClient(BASEURL, 'secret-key')
    assert client.remove_user_from_group('u1', 'g1') is True


@responses.activate
def test_remove_user_from_group_failure():
    responses.add(
        responses.DELETE,
        BASEURL + config.GALAXY_GROUP_EP + 'g1/users/u1',
        status=404)

    client = GalaxyClient(BASEURL, 'secret-key')
    assert client.remove_user_from_group('u1', 'g1') is False
