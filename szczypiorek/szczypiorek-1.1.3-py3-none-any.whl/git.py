
from bash import bash

from .exceptions import FileNotIgnoredError


def assert_is_git_ignored(filepath):
    if not filepath:
        return True

    result = bash(f'git check-ignore {filepath}')

    if result.stdout:
        return True

    else:
        raise FileNotIgnoredError(f"""
            Well it seems that the '{filepath}' is not git ignored. Since it
            appears in the context there's a big chance that it contains some
            sensitive data.

            Please add it to the '.gitignore' and stop tracking it.
        """)


def assert_is_git_repository():
    result = bash('ls .git')

    if result.stderr:
        return False

    return True
