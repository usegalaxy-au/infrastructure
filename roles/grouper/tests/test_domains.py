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


# -- Subdomain wildcards ----------------------------------------------------

def test_one_label_subdomain_matches_wildcard():
    rules = DomainRules({'Australian_government': ['*.gov.au']})
    assert rules.groups_for_email('a@health.gov.au') == [
        'Australian_government']


def test_multi_label_subdomain_matches_wildcard():
    rules = DomainRules({'Australian_government': ['*.gov.au']})
    assert rules.groups_for_email('a@dst.defence.gov.au') == [
        'Australian_government']


def test_bare_suffix_does_not_match_its_own_wildcard():
    rules = DomainRules({'Australian_government': ['*.gov.au']})
    assert rules.groups_for_email('a@gov.au') == []


@pytest.mark.parametrize('email', [
    'a@mygov.au',
    'a@notgov.au',
])
def test_lookalike_domain_does_not_match_wildcard(email):
    rules = DomainRules({'Australian_government': ['*.gov.au']})
    assert rules.groups_for_email(email) == []


def test_sibling_tld_does_not_match_wildcard():
    rules = DomainRules({'Australian_government': ['*.gov.au']})
    assert rules.groups_for_email('a@health.gov.nz') == []


def test_wildcard_matching_is_case_insensitive_both_ways():
    rules = DomainRules({'Australian_government': ['*.GOV.AU']})
    assert rules.groups_for_email('X@HEALTH.GOV.AU') == [
        'Australian_government']


@pytest.mark.parametrize('email', [
    'no-at-sign',
    'a@b@c',
    '',
    None,
])
def test_malformed_email_returns_no_groups_with_wildcards(email):
    rules = DomainRules({'Australian_government': ['*.gov.au']})
    assert rules.groups_for_email(email) == []
    assert not rules.domain_approved_for('Australian_government', email)


# -- Union semantics ---------------------------------------------------------

def test_exact_and_wildcard_in_different_groups_both_match():
    rules = DomainRules({
        'Wildcard Group': ['*.gov.au'],
        'Exact Group': ['health.gov.au'],
    })
    assert rules.groups_for_email('a@health.gov.au') == [
        'Exact Group', 'Wildcard Group']


def test_exact_and_wildcard_in_same_group_counted_once():
    rules = DomainRules({
        'Group A': ['*.gov.au', 'health.gov.au'],
    })
    assert rules.groups_for_email('a@health.gov.au') == ['Group A']


def test_multiple_wildcards_and_exact_all_match():
    rules = DomainRules({
        'Australian_government': ['*.gov.au'],
        'QLD_government': ['*.qld.gov.au'],
        'Agriculture': ['daf.qld.gov.au'],
    })
    assert rules.groups_for_email('a@daf.qld.gov.au') == [
        'Agriculture', 'Australian_government', 'QLD_government']


def test_five_rule_pile_up_returns_all_five_groups():
    rules = DomainRules({
        'Group 1': ['*.gov.au'],
        'Group 2': ['*.d.gov.au'],
        'Group 3': ['*.c.d.gov.au'],
        'Group 4': ['*.b.c.d.gov.au'],
        'Group 5': ['a.b.c.d.gov.au'],
    })
    assert rules.groups_for_email('a@a.b.c.d.gov.au') == [
        'Group 1', 'Group 2', 'Group 3', 'Group 4', 'Group 5']


def test_groups_for_email_result_is_sorted_and_duplicate_free():
    rules = DomainRules({
        'Zebra Group': ['*.gov.au'],
        'Alpha Group': ['*.gov.au'],
    })
    groups = rules.groups_for_email('a@health.gov.au')
    assert groups == sorted(groups)
    assert len(groups) == len(set(groups))


# -- Consistency between groups_for_email and domain_approved_for -----------

@pytest.mark.parametrize('email', [
    'a@health.gov.au',
    'a@dst.defence.gov.au',
    'a@gov.au',
    'a@mygov.au',
    'a@gov.nz',
    'a@daf.qld.gov.au',
])
def test_domain_approved_for_matches_groups_for_email(email):
    rules = DomainRules({
        'Australian_government': ['*.gov.au'],
        'QLD_government': ['*.qld.gov.au'],
        'Agriculture': ['daf.qld.gov.au'],
    })
    matched = set(rules.groups_for_email(email))
    for group in ('Australian_government', 'QLD_government', 'Agriculture'):
        assert rules.domain_approved_for(group, email) == (
            group in matched)


# -- Wildcard validation ------------------------------------------------------

@pytest.mark.parametrize('domain', [
    '*',
    '*.au',
    '*gov.au',
    'foo.*.au',
    '.gov.au',
])
def test_rejects_malformed_wildcard(domain):
    with pytest.raises(DomainRulesError):
        DomainRules({'Group A': [domain]})


def test_rejects_wildcard_with_empty_label():
    with pytest.raises(DomainRulesError):
        DomainRules({'Group A': ['*.gov..au']})


def test_leading_dot_error_message_suggests_wildcard():
    with pytest.raises(DomainRulesError) as exc_info:
        DomainRules({'Group A': ['.gov.au']})
    assert '*.gov.au' in str(exc_info.value)


def test_warns_on_same_wildcard_shared_across_groups(caplog):
    caplog.set_level(logging.WARNING)
    DomainRules({
        'Group A': ['*.gov.au'],
        'Group B': ['*.gov.au'],
    })
    assert '*.gov.au' in caplog.text
    assert 'multiple groups' in caplog.text


def test_does_not_warn_on_exact_domain_under_someone_elses_wildcard(caplog):
    caplog.set_level(logging.WARNING)
    DomainRules({
        'Wildcard Group': ['*.gov.au'],
        'Exact Group': ['health.gov.au'],
    })
    assert 'multiple groups' not in caplog.text


def test_does_not_warn_on_two_different_overlapping_wildcards(caplog):
    caplog.set_level(logging.WARNING)
    DomainRules({
        'Group A': ['*.gov.au'],
        'Group B': ['*.qld.gov.au'],
    })
    assert 'multiple groups' not in caplog.text


# -- No-wildcard regression ---------------------------------------------------

@pytest.mark.parametrize('email, expected', [
    ('alice@uq.edu.au', ['AU Researchers']),
    ('bob@shared.edu.au', ['Also Multi Group', 'Multi Group']),
    ('carol@nowhere.com', []),
    ('alice@student.uq.edu.au', []),
])
def test_no_wildcards_behaves_identically_to_exact_only(
    domains, email, expected,
):
    """A rules file with no wildcards is unaffected by this feature."""
    assert domains.groups_for_email(email) == expected
