import os

from dotenv import load_dotenv

load_dotenv()

STAGING_GALAXY_API_KEY = os.environ['STAGING_GALAXY_API_KEY']
STAGING_GALAXY_BASEURL = "https://staging.gvl.org.au/api/"
PROD_GALAXY_API_KEY = os.environ['PROD_GALAXY_API_KEY']
PROD_GALAXY_BASEURL = "https://usegalaxy.org.au/api/"

GALAXY_USER_EP = "users"
GALAXY_GROUP_EP = "groups/"
GALAXY_GROUP_USER_EP = "/users"

SLACK_TOKEN = os.environ['SLACK_TOKEN']
SLACK_ALERT_CHANNEL = "#alerts"
SLACK_LOG_CHANNEL = "#galaxy-logs"
SLACK_ALERT_MENTIONS = ""
SLACK_LOG_MENTIONS = ""
