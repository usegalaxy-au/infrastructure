"""Tests for grouper.domains.DomainRules."""
import logging

import pytest

from grouper.domains import DomainRules, DomainRulesError
from grouper.errors import GrouperUserError


def test_domain_maps_to_one_group(domains):
    assert domains.groups_for_email('alice@uq.edu.au') == ['AU Researchers']


def test_domain_maps_to_multiple_groups(domains):
    groups = domains.groups_for_email('bob@shared.edu.au')
    assert sorted(groups) == ['Also Multi Group', 'Multi Group']


def test_domain_maps_to_no_group(domains):
    assert domains.groups_for_email('carol@nowhere.com') == []


def test_case_insensitive_matching(domains):
    assert domains.groups_for_email('alice@UQ.EDU.AU') == ['AU Researchers']
    assert domains.domain_approved_for('AU Researchers', 'alice@UQ.EDU.AU')


def test_subdomains_do_not_match_parent_domain(domains):
    """See DomainRules docstring: subdomains must be listed explicitly."""
    assert domains.groups_for_email('alice@student.uq.edu.au') == []
    assert not domains.domain_approved_for(
        'AU Researchers', 'alice@student.uq.edu.au')


@pytest.mark.parametrize('email', [
    'no-at-sign',
    'a@b@c',
    '',
    None,
])
def test_malformed_email_returns_no_groups(domains, email):
    assert domains.groups_for_email(email) == []
    assert not domains.domain_approved_for('AU Researchers', email)


def test_unmanaged_group_is_not_managed(domains):
    assert not domains.is_managed('Some Group Not In Approved Domains')


def test_managed_group_is_managed(domains):
    assert domains.is_managed('AU Researchers')


def test_unmanaged_group_domain_never_approved(domains):
    assert not domains.domain_approved_for(
        'Some Group Not In Approved Domains', 'alice@uq.edu.au')


def test_from_file_loads_rules(tmp_path):
    path = tmp_path / 'approved_domains.json'
    path.write_text('{"Group A": ["example.com"]}')
    rules = DomainRules.from_file(path)
    assert rules.groups_for_email('x@example.com') == ['Group A']


def test_from_file_malformed_json_raises_clear_error(tmp_path):
    path = tmp_path / 'approved_domains.json'
    path.write_text('{"Group A": ["example.com"],}')  # trailing comma

    with pytest.raises(DomainRulesError) as exc_info:
        DomainRules.from_file(path)

    assert str(path) in str(exc_info.value)


def test_domain_rules_error_is_a_grouper_user_error():
    """main() catches the base class, so the subclass must derive from it."""
    assert issubclass(DomainRulesError, GrouperUserError)


# -- Stage 4: validation on load ------------------------------------------

def test_rejects_non_object_top_level():
    with pytest.raises(DomainRulesError):
        DomainRules(["not", "a", "dict"])


def test_rejects_non_list_group_value():
    with pytest.raises(DomainRulesError):
        DomainRules({'Group A': 'example.com'})


def test_rejects_non_string_domain():
    with pytest.raises(DomainRulesError):
        DomainRules({'Group A': [123]})


def test_rejects_email_looking_domain():
    with pytest.raises(DomainRulesError):
        DomainRules({'Group A': ['someone@example.com']})


def test_warns_on_domain_shared_across_groups(caplog):
    caplog.set_level(logging.WARNING)
    DomainRules({
        'Group A': ['shared.example.com'],
        'Group B': ['shared.example.com'],
    })
    assert 'shared.example.com' in caplog.text
    assert 'multiple groups' in caplog.text
