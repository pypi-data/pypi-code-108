"""Various constants used throughout the project."""

import re

YES_SET = {"y", "yes", "true", "on", "yep", "yeah", "ok"}
GIT_REGEX = re.compile(
    r"((git|ssh|http(s)?)|(git@[\w\.]+))(:(//)?)([\w\.@\:/\-~]+)(\.git)?(/)?"
)
RESERVED_DIR_NAMES = {
    "hooks",
    "__pycache__",
    ".git",
}
