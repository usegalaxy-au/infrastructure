"""Orchestrates checking, adding and removing Galaxy group members."""
import logging
from collections import defaultdict

from .domains import DomainRules
from .galaxy import GalaxyClient
from .params import Params
from .slack_notify import SlackNotifier
from .state import UserStateStore

logger = logging.getLogger(__name__)


class Grouper:
    """Runs one grouper pass: check users, add/remove, notify."""

    def __init__(
        self,
        params: Params,
        galaxy: GalaxyClient,
        slack: SlackNotifier,
        domains: DomainRules,
        state: UserStateStore,
    ):
        self._params = params
        self._galaxy = galaxy
        self._slack = slack
        self._domains = domains
        self._state = state

    def main(self) -> bool:
        """Fetch users, then generate initial state or run a full pass.

        Returns whether the invocation succeeded - `__main__` uses this to
        set the process exit code.
        """
        if self._params.production:
            logger.info("Production Galaxy server selected.")
        else:
            logger.info("Staging Galaxy server selected.")

        users = self._galaxy.get_users()

        if not users:
            logger.error("Unable to fetch users. Exiting without any work.")
            return False

        if self._params.generate:
            self._state.save([user.id for user in users])
            return True

        return self.run(users)

    def run(self, users: list) -> bool:
        """Check for user changes, then add/remove/notify as requested.

        Returns False if the run was refused by the change-limit safety
        valve (see identify_add_users/identify_remove_users totals below),
        True otherwise.
        """
        rem_users = {}
        add_users = {}

        groups = self._galaxy.get_groups()
        current_user_ids = sorted(user.id for user in users)

        self.warn_missing_groups(groups)

        if self.check_users(users, groups) and not self._params.all_users:
            logger.info(
                "No new users detected and all users flag not set. "
                "Exiting.")
            return True

        if self._params.list_domains:
            group_domains, no_email_users, bad_email_users = (
                self.list_group_domains(groups))

            if no_email_users:
                logger.info("Users with no email: %s", no_email_users)

            if bad_email_users:
                logger.info("Users with bad email: %s", bad_email_users)

            logger.info("Domains associated with groups: %s", group_domains)
            return True

        if self._params.remove:
            rem_users = self.identify_remove_users(groups, dummy=True)
            logger.info("Users to be removed from groups: %s", rem_users)

        if self._params.add:
            add_users = self.identify_add_users(users, groups, dummy=True)
            logger.info("Users to be added to groups: %s", add_users)

        total_changes = (
            sum(len(v) for v in rem_users.values())
            + sum(len(v) for v in add_users.values()))

        if (
            not self._params.dry_run
            and total_changes > self._params.limit
            and not self._params.force
        ):
            msg = (
                f"Refusing to act on {total_changes} group membership "
                f"changes in one run (limit is {self._params.limit}). "
                "Re-run with --force to proceed, or check "
                "approved_domains.json and the Galaxy user list for a "
                "truncation before doing so.")
            logger.error(msg)
            self._slack.notify(
                "Grouper safety valve triggered", msg, colour='danger')
            return False

        if not self._params.dry_run:
            if self._params.remove:
                self.identify_remove_users(groups)
            if self._params.add:
                self.identify_add_users(users, groups)

        if self._params.notify:
            if rem_users:
                self.notify_users(rem_users, users, groups, added=False)
            if add_users:
                self.notify_users(add_users, users, groups, added=True)

        # Saved last, so a failure anywhere above leaves the previous
        # state in place and those users get reprocessed next run.
        self._state.save(current_user_ids)
        return True

    def warn_missing_groups(self, groups: list) -> list:
        """Warn about managed groups that don't exist on this server.

        Groups are created by hand in Galaxy, so a name can be added to
        approved_domains.json before (or without) the group existing -
        most often on staging, which carries few groups. Those names are
        skipped rather than fatal; returns them for the caller's use.
        """
        existing = {group.name for group in groups}
        missing = [
            name for name in self._domains.managed_groups()
            if name not in existing
        ]

        if missing:
            logger.warning(
                "%d group/s in approved_domains.json do not exist on this "
                "Galaxy server and will be skipped: %s",
                len(missing), ', '.join(missing))

        return missing

    def check_users(self, users: list, groups: list) -> bool:
        """Diff current users against the saved state, notify on change.

        Returns True when there is no change since the last run.
        """
        current_user_ids = sorted(user.id for user in users)
        added, removed = self._state.diff(current_user_ids)

        if not added and not removed:
            return True

        if removed:
            logger.info("Newly removed users: %s", removed)
            if self._params.notify:
                self.notify_new_users(removed, users, groups, new=False)

        if added and self._params.notify:
            logger.info("Newly added users: %s", added)
            self.notify_new_users(added, users, groups, new=True)

        return False

    def identify_add_users(
        self, users: list, groups: list, dummy: bool = False,
    ) -> dict:
        """Work out which users should be added to which groups."""
        ret = defaultdict(list)
        group_by_name = {group.name: group for group in groups}

        for user in users:
            if user.email is None:
                logger.warning(
                    "No email associated with user: %s. Skipping", user)
                continue

            if user.email.count('@') != 1:
                logger.warning(
                    "Malformed email address for user: %s. Skipping", user)
                continue

            for group_name in self._domains.groups_for_email(user.email):
                group = group_by_name.get(group_name)

                if group is None:
                    # Named in approved_domains.json but absent from this
                    # Galaxy server - run() has already warned about it.
                    logger.debug(
                        "Skipping user %s for missing group '%s'",
                        user.id, group_name)
                    continue

                in_group = any(
                    guser.id == user.id for guser in group.users)

                if not in_group:
                    ret[user.email].append(group_name)
                    if not self._params.dry_run and not dummy:
                        # TODO add check for result here
                        self._galaxy.add_user_to_group(user.id, group.id)

        return dict(ret)

    def identify_remove_users(
        self, groups: list, dummy: bool = False,
    ) -> dict:
        """Work out which group members are no longer domain-eligible.

        Returns a dict keyed by user email (matching identify_add_users'
        shape) so notify_users can look delta users up the same way on
        both the add and remove paths.
        """
        ret = defaultdict(list)

        for group in groups:
            if not self._domains.is_managed(group.name):
                logger.warning(
                    "Group '%s' not set for automatic assignment. "
                    "Skipping", group.name)
                continue

            for user in group.users:
                if user.email is None or user.email.count('@') != 1:
                    logger.warning(
                        "Bad email for user %s. Skipping", user.id)
                    continue

                if not self._domains.domain_approved_for(
                    group.name, user.email,
                ):
                    ret[user.email].append(group.name)

                    if not self._params.dry_run and not dummy:
                        # TODO add check for result here
                        self._galaxy.remove_user_from_group(
                            user.id, group.id)

        return dict(ret)

    def notify_users(
        self, delta_users, users: list, groups: list, added: bool,
    ) -> None:
        """Notify Slack of users newly eligible/ineligible for groups."""
        msgs = []

        if added:
            title = "Users on Galaxy Australia now eligible for groups"
            colour = 'good'
        else:
            title = "Users on Galaxy Australia no longer eligible for groups"
            colour = 'warning'

        for delta_user in delta_users:
            user = next(x for x in users if x.email == delta_user)

            if added:
                assigned = self.identify_add_users(
                    [user], groups, dummy=True)
                if assigned:
                    group_list = ','.join(assigned[user.email])
                    if self._params.dry_run:
                        msgs.append(
                            f"{user.email} would be assigned to group/s: "
                            f"{group_list}")
                    else:
                        msgs.append(
                            f"{user.email} assigned to group/s: "
                            f"{group_list}")
            else:
                removed = self.identify_remove_users(groups, dummy=True)
                group_names = removed.get(user.email, [])
                if group_names:
                    group_list = ','.join(group_names)
                    if self._params.dry_run:
                        msgs.append(
                            f"{user.email} would be removed from group/s: "
                            f"{group_list}")
                    else:
                        msgs.append(
                            f"{user.email} removed from group/s: "
                            f"{group_list}")

        self._slack.notify(title, '\n'.join(msgs), colour)

    def notify_new_users(
        self, delta_users: list, users: list, groups: list, new: bool,
    ) -> None:
        """Notify Slack of newly detected or deleted Galaxy users."""
        msgs = []

        if new:
            title = "New users detected on Galaxy Australia"
            colour = 'good'
        else:
            title = "Detected deleted users on Galaxy Australia"
            colour = 'warning'

        for delta_user in delta_users:
            if not new:
                # Deleted users are, by definition, absent from `users` -
                # there is no email to look up. Report the id alone.
                msgs.append(f"User id {delta_user} removed")
                continue

            user = next(x for x in users if x.id == delta_user)
            assigned = self.identify_add_users([user], groups, dummy=True)
            if assigned:
                group_list = ','.join(assigned[user.email])
                if self._params.dry_run:
                    msgs.append(
                        f"{user.email} would be assigned to group/s: "
                        f"{group_list}")
                else:
                    msgs.append(
                        f"{user.email} to be assigned to group/s: "
                        f"{group_list}")
            else:
                if self._params.dry_run:
                    msgs.append(
                        f"{user.email} would not be assigned to any "
                        "automatic groups")
                else:
                    msgs.append(
                        f"{user.email} will not be assigned to any "
                        "automatic groups")

        self._slack.notify(title, '\n'.join(msgs), colour)

    def list_group_domains(self, groups: list) -> tuple:
        """Summarise the email domains currently seen in each group."""
        group_domains = {}
        no_email_users = []
        bad_email_users = []

        for group in groups:
            for user in group.users:
                if user.email is None:
                    no_email_users.append(user)
                    continue

                if user.email.count('@') != 1:
                    bad_email_users.append(user)
                    continue

                if group.name not in group_domains:
                    group_domains[group.name] = set()

                group_domains[group.name].add(user.email.split('@')[1])

        return group_domains, no_email_users, bad_email_users
