import datetime
import json
import os

from glapi import configuration as glapi_config

# FILE SYSTEM
FILEPATH_GITRICS_USER = os.environ["FILEPATH_GITRICS_USER"] if "FILEPATH_GITRICS_USER" in os.environ else None

# FOCI
FOCI = [d.strip() for d in os.environ["FOCI"].split(",")] if "FOCI" in os.environ else ["a", "b", "c", "d"]
FOCI_TERMS = None
if os.path.exists(os.path.join(os.getcwd(), "foci.json")):
    with open("foci.json", "r") as f:
        term_map = json.loads(f.read())
        FOCI_TERMS = dict()
        for key in term_map:
            for value in term_map[key]:
                FOCI_TERMS[value] = key

# GITLAB
# events
ACTIVITY_TYPES = {
    "coding": ["pushed", "merged"],
    "collaboration": ["approved", "closed", "commented", "created", "updated"]
}

# filters
FILTER_GROUP_NAMESPACES = [d.strip() for d in os.environ["FILTER_GITLAB_GROUP_NAMESPACES"].split(",")] if "FILTER_GITLAB_GROUP_NAMESPACES" in os.environ else list()
FILTER_PROJECT_IDS = [d.strip() for d in os.environ["FILTER_GITLAB_PROJECT_IDS"].split(",")] if "FILTER_GITLAB_PROJECT_IDS" in os.environ else list()
FILTER_PROJECT_NAMES = [d.strip() for d in os.environ["FILTER_GITLAB_PROJECT_NAMES"].split(",")] if "FILTER_GITLAB_PROJECT_NAMES" in os.environ else list()
FILTER_PROJECT_NAMES_STARTSWITH = [d.strip() for d in os.environ["FILTER_GITLAB_PROJECT_NAMES_STARTSWITH"].split(",")] if "FILTER_GITLAB_PROJECT_NAMES_STARTSWITH" in os.environ else list()

# instance
GITLAB_TOKEN = glapi_config.GITLAB_TOKEN
GITLAB_API_VERSION = glapi_config.GITLAB_API_VERSION
GITLAB_NAME = os.environ["GITLAB_NAME"] if "GITLAB_NAME" in os.environ else "GitLab"
GITLAB_NAMESPACE = os.environ["GITLAB_NAMESPACE"] if "GITLAB_NAMESPACE" in os.environ else None
GITLAB_URL = os.environ["GITLAB_URL"] if "GITLAB_URL" in os.environ else "https://gitlab.com"

# projects
MEMBERSHIP = glapi_config.GITLAB_PROJECT_USER_MEMBERSHIP
PERSONAL = glapi_config.GITLAB_PROJECT_PERSONAL_ONLY
SIMPLE = glapi_config.GITLAB_PROJECT_SIMPLE
VISIBILITY = glapi_config.GITLAB_PROJECT_VISIBILITY

# users
USER = os.environ["GITLAB_USER_ID"] if "GITLAB_USER_ID" in os.environ else None
USER_ACCESS = os.environ["GITLAB_USER_PROJECT_ACCESS"] if "GITLAB_USER_PROJECT_ACCESS" in os.environ else 30
USER_ACCESS_LEVELS = {
    30: "developer",
    40: "maintainer",
    50: "owner"
}

# TIME
DATE_ISO_8601 = glapi_config.DATE_ISO_8601
