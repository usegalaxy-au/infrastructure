"""Email-domain to group eligibility rules."""
import json
from collections import defaultdict
from pathlib import Path
from typing import Optional


class DomainRules:
    """Owns the group -> approved domains mapping, and its inverse.

    Domain matching is case-insensitive but exact: a subdomain (e.g.
    `student.uq.edu.au`) does not match unless it is itself listed
    alongside its parent domain (`uq.edu.au`).
    """

    def __init__(self, approved_domains: dict):
        self._approved_domains = approved_domains
        self._domains_by_group = {
            group: {domain.lower() for domain in domains}
            for group, domains in approved_domains.items()
        }
        self._groups_by_domain = self._invert(self._domains_by_group)

    @classmethod
    def from_file(cls, path: Path) -> 'DomainRules':
        """Load approved domain rules from a JSON file."""
        with open(path) as f:
            return cls(json.load(f))

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
