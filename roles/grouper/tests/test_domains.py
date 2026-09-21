"""Tests for grouper.domains.DomainRules."""
import pytest

from grouper.domains import DomainRules


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
