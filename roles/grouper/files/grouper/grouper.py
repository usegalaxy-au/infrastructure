"""Orchestrates checking, adding and removing Galaxy group members."""
from collections import defaultdict

from .domains import DomainRules
from .galaxy import GalaxyClient
from .params import Params
from .slack_notify import SlackNotifier
from .state import UserStateStore


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

    def main(self) -> None:
        """Fetch users, then generate initial state or run a full pass."""
        if self._params.production:
            print("Production Galaxy server selected.")
        else:
            print("Staging Galaxy server selected.")

        users = self._galaxy.get_users()

        if not users:
            print("Unable to fetch users. Quiting without any work.")
            return

        if self._params.generate:
            self._state.save([user.id for user in users])
            return

        self.run(users)

    def run(self, users: list) -> None:
        """Check for user changes, then add/remove/notify as requested."""
        rem_users = {}
        add_users = {}

        groups = self._galaxy.get_groups()
        current_user_ids = sorted(user.id for user in users)

        if self.check_users(users, groups) and not self._params.all_users:
            print("No new users detected and all users flag not set. "
                  "Exiting.")
            return

        if self._params.list_domains:
            group_domains, no_email_users, bad_email_users = (
                self.list_group_domains(groups))

            if no_email_users:
                print("Users with no email:")
                print(no_email_users)

            if bad_email_users:
                print("Users with bad email:")
                print(bad_email_users)

            print("Domains associated with groups:")
            print(group_domains)
            return

        if self._params.remove:
            rem_users = self.identify_remove_users(groups)
            print("Users to be removed from groups:")
            print(rem_users)

        if self._params.add:
            add_users = self.identify_add_users(users, groups)
            print("Users to be added to groups:")
            print(add_users)

        if self._params.notify:
            if rem_users:
                self.notify_users(rem_users, users, groups, added=False)
            if add_users:
                self.notify_users(add_users, users, groups, added=True)

        # Saved last, so a failure anywhere above leaves the previous
        # state in place and those users get reprocessed next run.
        self._state.save(current_user_ids)

    def check_users(self, users: list, groups: list) -> bool:
        """Diff current users against the saved state, notify on change.

        Returns True when there is no change since the last run.
        """
        current_user_ids = sorted(user.id for user in users)
        added, removed = self._state.diff(current_user_ids)

        if not added and not removed:
            return True

        if removed:
            print("Newly removed users: ")
            print(removed)
            if self._params.notify:
                self.notify_new_users(removed, users, groups, new=False)

        if added and self._params.notify:
            print("Newly added users:")
            print(added)
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
                print(f"No email associated with user: {user}. Skipping")
                continue

            if user.email.count('@') != 1:
                print(
                    f"Malformed email address for user: {user}. Skipping")
                continue

            for group_name in self._domains.groups_for_email(user.email):
                group = group_by_name[group_name]
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
                print(
                    f"Group '{group.name}' not set for automatic "
                    "assignment. Skipping")
                continue

            for user in group.users:
                if user.email is None or user.email.count('@') != 1:
                    print(f"Bad email for user {user.id}. Skipping")
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
