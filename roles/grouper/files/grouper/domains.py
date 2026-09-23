"""Email-domain to group eligibility rules."""
import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Optional

from .errors import GrouperUserError

logger = logging.getLogger(__name__)

WILDCARD_PREFIX = '*.'
MIN_WILDCARD_LABELS = 2


class DomainRulesError(GrouperUserError):
    """Raised when approved_domains.json is not well-formed."""


class DomainRules:
    """Owns the group -> approved domains mapping, and its inverse.

    Domain matching is case-insensitive. Most entries are exact: a
    subdomain (e.g. `student.uq.edu.au`) does not match unless it is
    itself listed alongside its parent domain (`uq.edu.au`). An entry
    written as `*.suffix` (e.g. `*.gov.au`) is a wildcard and matches
    any domain with one or more labels under that suffix - the bare
    suffix itself does not match its own wildcard.

    A user is assigned to every group whose rules match their email
    domain: the result is the plain union of the exact match and all
    matching wildcards, with no precedence between them.
    """

    def __init__(self, approved_domains: dict):
        self._validate(approved_domains)
        self._approved_domains = approved_domains
        self._exact_by_group = {
            group: {
                domain.lower() for domain in domains
                if not domain.startswith(WILDCARD_PREFIX)
            }
            for group, domains in approved_domains.items()
        }
        self._wildcards_by_group = {
            group: {
                domain.lower()[len(WILDCARD_PREFIX):] for domain in domains
                if domain.startswith(WILDCARD_PREFIX)
            }
            for group, domains in approved_domains.items()
        }
        self._groups_by_domain = self._invert(self._exact_by_group)
        self._groups_by_wildcard = self._invert(self._wildcards_by_group)
        self._warn_on_shared_domains()

    @classmethod
    def from_file(cls, path: Path) -> 'DomainRules':
        """Load approved domain rules from a JSON file."""
        with open(path) as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise DomainRulesError(
                    f"{path} is not valid JSON: {e}") from e
        return cls(data)

    @staticmethod
    def _validate(approved_domains: dict) -> None:
        if not isinstance(approved_domains, dict):
            raise DomainRulesError(
                "approved_domains.json must be a JSON object mapping "
                "group names to lists of domains")

        for group, domains in approved_domains.items():
            if not isinstance(domains, list) or not all(
                isinstance(domain, str) for domain in domains
            ):
                raise DomainRulesError(
                    f"Group '{group}' must map to a list of domain "
                    "strings")

            for domain in domains:
                if '@' in domain:
                    raise DomainRulesError(
                        f"Domain '{domain}' for group '{group}' looks "
                        "like an email address - list bare domains "
                        "(e.g. 'uq.edu.au'), not '@'-addresses")

                DomainRules._validate_wildcard(domain, group)

    @staticmethod
    def _validate_wildcard(domain: str, group: str) -> None:
        if domain.startswith('.'):
            raise DomainRulesError(
                f"Domain '{domain}' for group '{group}' starts with a "
                f"dot - did you mean '*{domain}'?")

        if domain == '*':
            raise DomainRulesError(
                f"Domain '*' for group '{group}' would approve every "
                "user on the server")

        if not domain.startswith(WILDCARD_PREFIX):
            if '*' in domain:
                raise DomainRulesError(
                    f"Domain '{domain}' for group '{group}' is malformed "
                    "- '*' is only meaningful as a leading "
                    f"'{WILDCARD_PREFIX}' label")
            return

        suffix = domain[len(WILDCARD_PREFIX):]
        labels = suffix.split('.')

        if '*' in suffix or '' in labels:
            raise DomainRulesError(
                f"Domain '{domain}' for group '{group}' is malformed")

        if len(labels) < MIN_WILDCARD_LABELS:
            raise DomainRulesError(
                f"Domain '{domain}' for group '{group}' has too few "
                "labels after the wildcard - this would match a public "
                "suffix and is almost certainly a mistake")

    def _warn_on_shared_domains(self) -> None:
        # Legal - a domain can grant several groups - but usually a typo.
        # Only the *same* exact domain or *same* wildcard string repeated
        # across groups is a likely typo; an exact domain overlapping with
        # someone else's wildcard, or two different wildcards overlapping,
        # is normal union behaviour and not warned on here.
        for domain, groups in self._groups_by_domain.items():
            if len(groups) > 1:
                logger.warning(
                    "Domain '%s' is approved for multiple groups: %s - "
                    "confirm this is intentional.",
                    domain, ', '.join(sorted(groups)))

        for wildcard, groups in self._groups_by_wildcard.items():
            if len(groups) > 1:
                logger.warning(
                    "Domain '%s%s' is approved for multiple groups: %s - "
                    "confirm this is intentional.",
                    WILDCARD_PREFIX, wildcard, ', '.join(sorted(groups)))

    @staticmethod
    def _invert(domains_by_group: dict) -> dict:
        inverse = defaultdict(list)
        for group, domains in domains_by_group.items():
            for domain in domains:
                inverse[domain].append(group)
        return dict(inverse)

    def groups_for_email(self, email: str) -> list:
        """Return every group name this email domain qualifies for.

        A user is assigned to every group whose rules match: the plain
        union of the exact match and all matching wildcards, with no
        precedence between them.
        """
        domain = self._domain(email)
        if domain is None:
            return []

        groups = set(self._groups_by_domain.get(domain, []))
        for suffix, wildcard_groups in self._groups_by_wildcard.items():
            if domain.endswith(f'.{suffix}'):
                groups.update(wildcard_groups)
        return sorted(groups)

    def domain_approved_for(self, group_name: str, email: str) -> bool:
        """Whether this email's domain is approved for the given group."""
        return group_name in self.groups_for_email(email)

    def is_managed(self, group_name: str) -> bool:
        """Whether this group is under automatic assignment."""
        return group_name in self._approved_domains

    def managed_groups(self) -> list:
        """Every group name under automatic assignment."""
        return sorted(self._approved_domains)

    @staticmethod
    def _domain(email: str) -> Optional[str]:
        if not email or email.count('@') != 1:
            return None
        return email.split('@')[1].lower()
