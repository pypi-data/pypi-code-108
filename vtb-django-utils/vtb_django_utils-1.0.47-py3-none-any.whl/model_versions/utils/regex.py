import re

from vtb_django_utils.model_versions.utils.consts import VERSION_DELIMITER


def version_regex(version: str):
    regex = r'^'
    parts = version.split(VERSION_DELIMITER)
    for i, part in enumerate(parts):
        if not part:
            continue
        regex += rf'{re.escape(part)}'
        regex += '.?' if i == 2 else r'\.'
    return regex
