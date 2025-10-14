import logging
from typing import Any

from galaxy.model import UserAuthnzToken, UserRoleAssociation, Group
from galaxy.model.db.user import User
from galaxy.model.db.role import Role
from galaxy.model.security import GalaxyRBACAgent

log = logging.getLogger(__name__)


ROLES_CLAIM = "https://biocommons.org.au/roles"
ROLES_PREFIX = "biocommons/group"
REMOVE_GROUPS = True


def get_groups_from_oidc_roles(roles: list[str]) -> list[str]:
    """
    Given a list of roles from Auth0, return a list of the groups
    included, based on ROLES_PREFIX.
    """
    return [role for role in roles if role.startswith(ROLES_PREFIX)]


def sync_user_groups(user: User = None, access_token: dict[str, Any] = None, social: UserAuthnzToken = None, **kwargs):
    """
    Pipeline step to sync user groups from Auth0.
    """
    roles: list[str] = access_token.get(ROLES_CLAIM)
    if roles is None:
        log.debug("No roles claim in access token")
        return

    auth0_group_names: list[str] = get_groups_from_oidc_roles(roles)
    user_group_names: list[str] = [assoc.group.name for assoc in user.groups
                                   if assoc.group.name.startswith(ROLES_PREFIX)]
    # In access token but not in user's groups
    groups_to_add: list[str] = [group_name for group_name in auth0_group_names
                                if group_name not in user_group_names]

    if groups_to_add:
        # Use RBAC API to handle changes where possible
        rbac = GalaxyRBACAgent(sa_session=social.sa_session)

        log.info(f"Adding groups from access token for user {user.id}: {groups_to_add}")
        for group_name in groups_to_add:
            group = (social.sa_session.query(Group)
                     .filter_by(name=group_name).one_or_none())
            if group is not None:
                rbac.associate_user_group(user=user, group=group)
            else:
                log.warning(f"Group {group_name} not found in Galaxy")

    # Remove BioCommons groups from user if not in access token
    if REMOVE_GROUPS:
        group_associations_to_remove = [assoc for assoc in user.groups
                                        if assoc.group.name.startswith(ROLES_PREFIX) and
                                        assoc.group.name not in auth0_group_names]
        remove_names = [assoc.group.name for assoc in group_associations_to_remove]
        if group_associations_to_remove:
            log.info(f"Removing groups from user {user.id}: {remove_names}")

            for group in group_associations_to_remove:
                social.sa_session.delete(group)
            social.sa_session.commit()


