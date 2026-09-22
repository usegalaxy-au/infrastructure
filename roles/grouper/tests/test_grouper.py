"""Tests for grouper.grouper.Grouper."""
import logging
from dataclasses import replace

import pytest

from grouper.grouper import Grouper
from grouper.state import UserStateStore


# -- identify_add_users ------------------------------------------------

def test_identify_add_users_skips_existing_membership(
    grouper, make_user, make_group,
):
    user = make_user('u1', 'alice@uq.edu.au')
    group = make_group('g1', 'AU Researchers', users=[user])

    assert grouper.identify_add_users([user], [group]) == {}


def test_identify_add_users_adds_only_missing_groups(
    grouper, make_user, make_group,
):
    user = make_user('u1', 'bob@shared.edu.au')  # eligible for two groups
    already_in = make_group('g1', 'Multi Group', users=[user])
    missing_from = make_group('g2', 'Also Multi Group', users=[])

    ret = grouper.identify_add_users([user], [already_in, missing_from])

    assert ret == {'bob@shared.edu.au': ['Also Multi Group']}


def test_identify_add_users_skips_group_missing_from_galaxy(
    grouper, fake_galaxy, make_user,
):
    """A group named in approved_domains.json but absent from the Galaxy
    server is skipped, not a KeyError. Hit on staging, which carries
    few/no groups.
    """
    user = make_user('u1', 'alice@uq.edu.au')

    assert grouper.identify_add_users([user], []) == {}
    assert fake_galaxy.add_calls == []


def test_warn_missing_groups_names_the_absent_groups(
    grouper, make_group, caplog,
):
    caplog.set_level(logging.WARNING)
    present = make_group('g1', 'AU Researchers', users=[])

    missing = grouper.warn_missing_groups([present])

    assert 'AU Researchers' not in missing
    assert missing  # the rest of the test rules are unrepresented
    assert 'do not exist on this Galaxy server' in caplog.text


def test_run_with_no_groups_on_server_does_not_raise(
    params, make_galaxy, fake_slack, domains, make_user,
):
    """The reported staging failure end to end: 0 groups on the server."""
    user = make_user('u1', 'alice@uq.edu.au')
    galaxy = make_galaxy(groups=[], users=[user])

    state = UserStateStore(params.grouper_dir / 'users.json')
    state.save([])
    p = replace(params, add=True, remove=True, all_users=True)
    grouper = Grouper(p, galaxy, fake_slack, domains, state)

    assert grouper.run([user]) is True
    assert galaxy.add_calls == []


# -- identify_remove_users (Stage 3 bug 1, fixed) ------------------------

def test_identify_remove_users_processes_every_group(
    grouper, make_user, make_group,
):
    """Stage 3 bug 1 (fixed): every group is processed, not just the
    first. Keyed by user email, matching identify_add_users' shape.
    """
    ineligible1 = make_user('u1', 'alice@nowhere.com')
    ineligible2 = make_user('u2', 'bob@nowhere.com')
    group1 = make_group('g1', 'AU Researchers', users=[ineligible1])
    group2 = make_group('g2', 'Staff', users=[ineligible2])

    ret = grouper.identify_remove_users([group1, group2], dummy=True)

    assert ret == {
        'alice@nowhere.com': ['AU Researchers'],
        'bob@nowhere.com': ['Staff'],
    }


def test_identify_remove_users_skips_unmanaged_group(
    grouper, make_user, make_group,
):
    ineligible = make_user('u1', 'alice@nowhere.com')
    group = make_group('g1', 'Not Approved', users=[ineligible])

    assert grouper.identify_remove_users([group], dummy=True) == {}


# -- dry-run: the single most important test in the suite --------------

def test_dry_run_makes_zero_galaxy_calls(
    grouper, fake_galaxy, make_user, make_group,
):
    new_user = make_user('u1', 'alice@uq.edu.au')
    empty_group = make_group('g1', 'AU Researchers', users=[])
    grouper.identify_add_users([new_user], [empty_group])

    ineligible = make_user('u2', 'carol@nowhere.com')
    group_with_ineligible = make_group(
        'g2', 'AU Researchers', users=[ineligible])
    grouper.identify_remove_users([group_with_ineligible])

    assert fake_galaxy.add_calls == []
    assert fake_galaxy.remove_calls == []


def test_commit_run_calls_galaxy(
    params, fake_galaxy, fake_slack, domains, make_user, make_group,
):
    p = replace(params, dry_run=False)
    state = UserStateStore(p.grouper_dir / 'users.json')
    grouper = Grouper(p, fake_galaxy, fake_slack, domains, state)

    user = make_user('u1', 'alice@uq.edu.au')
    group = make_group('g1', 'AU Researchers', users=[])

    grouper.identify_add_users([user], [group])

    assert fake_galaxy.add_calls == [('u1', 'g1')]


# -- run(): --all forces a pass even when the user list is unchanged ---

def test_all_users_flag_forces_pass_even_when_unchanged(
    params, make_galaxy, fake_slack, domains, make_user, make_group, caplog,
):
    caplog.set_level(logging.INFO)
    user = make_user('u1', 'alice@uq.edu.au')
    group = make_group('g1', 'AU Researchers', users=[])
    galaxy = make_galaxy(groups=[group], users=[user])

    state = UserStateStore(params.grouper_dir / 'users.json')
    state.save(['u1'])  # already seen - diff() is empty

    p = replace(params, add=True, all_users=True)
    grouper = Grouper(p, galaxy, fake_slack, domains, state)
    grouper.run([user])

    assert 'Users to be added to groups' in caplog.text
    assert 'alice@uq.edu.au' in caplog.text


def test_without_all_users_flag_unchanged_users_short_circuit(
    params, make_galaxy, fake_slack, domains, make_user, make_group, caplog,
):
    caplog.set_level(logging.INFO)
    user = make_user('u1', 'alice@uq.edu.au')
    group = make_group('g1', 'AU Researchers', users=[])
    galaxy = make_galaxy(groups=[group], users=[user])

    state = UserStateStore(params.grouper_dir / 'users.json')
    state.save(['u1'])

    p = replace(params, add=True, all_users=False)
    grouper = Grouper(p, galaxy, fake_slack, domains, state)
    grouper.run([user])

    assert 'No new users detected' in caplog.text
    assert 'Users to be added to groups' not in caplog.text


# -- notify_users / notify_new_users message text -----------------------

def test_notify_users_newly_eligible_dry_run(
    grouper, fake_slack, make_user, make_group,
):
    user = make_user('u1', 'alice@uq.edu.au')
    group = make_group('g1', 'AU Researchers', users=[])

    grouper.notify_users([user.email], [user], [group], added=True)

    title, msg, colour = fake_slack.notifications[0]
    assert title == 'Users on Galaxy Australia now eligible for groups'
    assert colour == 'good'
    assert 'would be assigned to group/s: AU Researchers' in msg


def test_notify_new_users_no_eligible_group_dry_run(
    grouper, fake_slack, make_user,
):
    user = make_user('u1', 'dave@nowhere.com')

    grouper.notify_new_users(['u1'], [user], [], new=True)

    title, msg, colour = fake_slack.notifications[0]
    assert title == 'New users detected on Galaxy Australia'
    assert colour == 'good'
    assert 'would not be assigned to any automatic groups' in msg


def test_notify_users_removal_colour_is_warning_not_warn(grouper, fake_slack):
    """Stage 1 fix: Slack colour was the literal 'warn', not a valid
    attachment colour. delta_users=[] isolates the colour fix from the
    removal message-text behaviour covered elsewhere.
    """
    grouper.notify_users([], [], [], added=False)

    title, msg, colour = fake_slack.notifications[0]
    assert title == 'Users on Galaxy Australia no longer eligible for groups'
    assert colour == 'warning'


def test_notify_new_users_deleted_colour_is_warning_not_warn(
    grouper, fake_slack,
):
    grouper.notify_new_users([], [], [], new=False)

    title, msg, colour = fake_slack.notifications[0]
    assert title == 'Detected deleted users on Galaxy Australia'
    assert colour == 'warning'


# -- Stage 3 bugs 2 and 3, fixed: no more StopIteration ------------------

def test_notify_users_removal_path_reports_removed_groups(
    grouper, fake_slack, make_user, make_group,
):
    """Stage 3 bug 2 (fixed): rem_users is now keyed by email, matching
    add_users' shape, so the lookup by email succeeds.
    """
    user = make_user('u1', 'alice@nowhere.com')
    group = make_group('g1', 'AU Researchers', users=[user])

    grouper.notify_users([user.email], [user], [group], added=False)

    title, msg, colour = fake_slack.notifications[0]
    assert 'would be removed from group/s: AU Researchers' in msg


def test_notify_new_users_deleted_user_reports_id_not_email(
    grouper, fake_slack,
):
    """Stage 3 bug 3 (fixed): a deleted user has no entry in `users`, so
    notify_new_users no longer looks them up by id - it reports the id.
    """
    grouper.notify_new_users(['u-deleted'], [], [], new=False)

    title, msg, colour = fake_slack.notifications[0]
    assert msg == 'User id u-deleted removed'


# -- Stage 3 bug 4, fixed: state is saved at the end of a successful run -

def test_check_users_does_not_save_state(
    params, fake_galaxy, fake_slack, domains, make_user,
):
    """Stage 3 bug 4 (fixed): check_users no longer saves state itself -
    that moved to the end of run(), so a failure in notify (or in
    add/remove, later in run()) leaves the previous state in place and
    those users are retried next run.
    """
    state = UserStateStore(params.grouper_dir / 'users.json')
    state.save(['u1'])

    p = replace(params, notify=True)
    grouper = Grouper(p, fake_galaxy, fake_slack, domains, state)

    def boom(*args, **kwargs):
        raise RuntimeError('simulated failure')

    grouper._slack.notify = boom

    users = [make_user('u1'), make_user('u2', 'carol@nowhere.com')]

    with pytest.raises(RuntimeError):
        grouper.check_users(users, [])

    assert state.load() == ['u1']


def test_run_saves_state_after_a_successful_pass(
    params, fake_galaxy, fake_slack, domains, make_user, make_group,
):
    state = UserStateStore(params.grouper_dir / 'users.json')
    state.save(['u1'])

    p = replace(params, add=True)
    grouper = Grouper(p, fake_galaxy, fake_slack, domains, state)

    user1 = make_user('u1', 'alice@uq.edu.au')
    user2 = make_user('u2', 'bob@uq.edu.au')
    group = make_group('g1', 'AU Researchers', users=[])

    fake_galaxy._groups = [group]

    grouper.run([user1, user2])

    assert state.load() == ['u1', 'u2']


# -- Stage 4: --limit safety valve ---------------------------------------

def test_limit_blocks_commit_and_alerts_slack(
    params, fake_galaxy, fake_slack, domains, make_user, make_group,
):
    state = UserStateStore(params.grouper_dir / 'users.json')
    state.save(['u1'])

    p = replace(params, dry_run=False, add=True, all_users=True, limit=1)
    grouper = Grouper(p, fake_galaxy, fake_slack, domains, state)

    user1 = make_user('u1', 'alice@uq.edu.au')
    user2 = make_user('u2', 'bob@uq.edu.au')
    group = make_group('g1', 'AU Researchers', users=[])
    fake_galaxy._groups = [group]

    ok = grouper.run([user1, user2])

    assert ok is False
    assert fake_galaxy.add_calls == []
    title, msg, colour = fake_slack.notifications[0]
    assert title == 'Grouper safety valve triggered'
    assert 'Refusing to act on 2' in msg
    # Blocked runs must not commit state, so the same users are retried.
    assert state.load() == ['u1']


def test_force_overrides_the_limit(
    params, fake_galaxy, fake_slack, domains, make_user, make_group,
):
    state = UserStateStore(params.grouper_dir / 'users.json')
    state.save(['u1'])

    p = replace(
        params, dry_run=False, add=True, all_users=True, limit=1, force=True,
    )
    grouper = Grouper(p, fake_galaxy, fake_slack, domains, state)

    user1 = make_user('u1', 'alice@uq.edu.au')
    user2 = make_user('u2', 'bob@uq.edu.au')
    group = make_group('g1', 'AU Researchers', users=[])
    fake_galaxy._groups = [group]

    ok = grouper.run([user1, user2])

    assert ok is True
    assert sorted(fake_galaxy.add_calls) == [('u1', 'g1'), ('u2', 'g1')]
    assert state.load() == ['u1', 'u2']


def test_limit_does_not_apply_in_dry_run(
    params, fake_galaxy, fake_slack, domains, make_user, make_group,
):
    state = UserStateStore(params.grouper_dir / 'users.json')
    state.save(['u1'])

    p = replace(params, dry_run=True, add=True, all_users=True, limit=1)
    grouper = Grouper(p, fake_galaxy, fake_slack, domains, state)

    user1 = make_user('u1', 'alice@uq.edu.au')
    user2 = make_user('u2', 'bob@uq.edu.au')
    group = make_group('g1', 'AU Researchers', users=[])
    fake_galaxy._groups = [group]

    ok = grouper.run([user1, user2])

    assert ok is True
    assert fake_galaxy.add_calls == []
    assert fake_slack.notifications == []


def test_check_users_no_change_returns_true(grouper, make_user):
    state = grouper._state
    state.save(['u1'])

    assert grouper.check_users([make_user('u1')], []) is True


# -- list_group_domains --------------------------------------------------

def test_list_group_domains_separates_bad_and_missing_emails(
    grouper, make_user, make_group,
):
    good = make_user('u1', 'alice@uq.edu.au')
    no_email = make_user('u2', None)
    bad_email = make_user('u3', 'not-an-email')
    group = make_group(
        'g1', 'AU Researchers', users=[good, no_email, bad_email])

    group_domains, no_email_users, bad_email_users = (
        grouper.list_group_domains([group]))

    assert group_domains == {'AU Researchers': {'uq.edu.au'}}
    assert no_email_users == [no_email]
    assert bad_email_users == [bad_email]
