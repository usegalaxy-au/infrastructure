"""Email-domain to group eligibility rules."""
import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class DomainRulesError(ValueError):
    """Raised when approved_domains.json is not well-formed."""


class DomainRules:
    """Owns the group -> approved domains mapping, and its inverse.

    Domain matching is case-insensitive but exact: a subdomain (e.g.
    `student.uq.edu.au`) does not match unless it is itself listed
    alongside its parent domain (`uq.edu.au`).
    """

    def __init__(self, approved_domains: dict):
        self._validate(approved_domains)
        self._approved_domains = approved_domains
        self._domains_by_group = {
            group: {domain.lower() for domain in domains}
            for group, domains in approved_domains.items()
        }
        self._groups_by_domain = self._invert(self._domains_by_group)
        self._warn_on_shared_domains()

    @classmethod
    def from_file(cls, path: Path) -> 'DomainRules':
        """Load approved domain rules from a JSON file."""
        with open(path) as f:
            return cls(json.load(f))

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

    def _warn_on_shared_domains(self) -> None:
        # Legal - a domain can grant several groups - but usually a typo.
        for domain, groups in self._groups_by_domain.items():
            if len(groups) > 1:
                logger.warning(
                    "Domain '%s' is approved for multiple groups: %s - "
                    "confirm this is intentional.",
                    domain, ', '.join(sorted(groups)))

    @staticmethod
    def _invert(domains_by_group: dict) -> dict:
        inverse = defaultdict(list)
        for group, domains in domains_by_group.items():
            for domain in domains:
                inverse[domain].append(group)
        return dict(inverse)

    def groups_for_email(self, email: str) -> list:
        """Return group names this email domain qualifies for."""
        domain = self._domain(email)
        if domain is None:
            return []
        return list(self._groups_by_domain.get(domain, []))

    def domain_approved_for(self, group_name: str, email: str) -> bool:
        """Whether this email's domain is approved for the given group."""
        domain = self._domain(email)
        if domain is None:
            return False
        return domain in self._domains_by_group.get(group_name, set())

    def is_managed(self, group_name: str) -> bool:
        """Whether this group is under automatic assignment."""
        return group_name in self._approved_domains

    @staticmethod
    def _domain(email: str) -> Optional[str]:
        if not email or email.count('@') != 1:
            return None
        return email.split('@')[1].lower()
