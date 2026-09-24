import os

from dotenv import load_dotenv

from grouper.errors import GrouperUserError

load_dotenv()

REQUIRED_ENV_VARS = [
    'STAGING_GALAXY_API_KEY',
    'STAGING_GALAXY_BASEURL',
    'PROD_GALAXY_API_KEY',
    'PROD_GALAXY_BASEURL',
    'SLACK_TOKEN',
    'SLACK_ALERT_CHANNEL',
    'SLACK_LOG_CHANNEL',
    'SLACK_ALERT_MENTIONS',
    'SLACK_LOG_MENTIONS',
]


class ConfigError(GrouperUserError):
    """Raised when a required environment variable is not set."""


def check_required_vars() -> None:
    """Raise ConfigError listing any required env var/s that are unset.

    The values below are read with os.environ.get (not `[...]`), so a
    missing .env doesn't crash on import - before logging is configured
    there's nowhere clean to report it. __main__ calls this once logging
    is set up, so a missing var is one ERROR line instead of a bare
    KeyError traceback.
    """
    missing = [
        name for name in REQUIRED_ENV_VARS
        if os.environ.get(name) is None]

    if missing:
        raise ConfigError(
            "Missing required environment variable/s (check .env): "
            + ', '.join(missing))


STAGING_GALAXY_API_KEY = os.environ.get('STAGING_GALAXY_API_KEY')
STAGING_GALAXY_BASEURL = os.environ.get('STAGING_GALAXY_BASEURL')
PROD_GALAXY_API_KEY = os.environ.get('PROD_GALAXY_API_KEY')
PROD_GALAXY_BASEURL = os.environ.get('PROD_GALAXY_BASEURL')

GALAXY_USER_EP = "users"
GALAXY_GROUP_EP = "groups/"
GALAXY_GROUP_USER_EP = "/users"

SLACK_TOKEN = os.environ.get('SLACK_TOKEN')
SLACK_ALERT_CHANNEL = os.environ.get('SLACK_ALERT_CHANNEL')
SLACK_LOG_CHANNEL = os.environ.get('SLACK_LOG_CHANNEL')
SLACK_ALERT_MENTIONS = os.environ.get('SLACK_ALERT_MENTIONS')
SLACK_LOG_MENTIONS = os.environ.get('SLACK_LOG_MENTIONS')
