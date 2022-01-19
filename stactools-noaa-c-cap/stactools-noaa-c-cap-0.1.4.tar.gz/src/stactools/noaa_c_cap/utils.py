from typing import List

import pkg_resources


def urls() -> List[str]:
    """Returns the list of URLs defined in urllist-modres.txt.

    These are URLs to _all_ of the NOAA C-CAP data and metadata files.
    """
    return pkg_resources.resource_string(
        __name__, 'urllist-modres.txt').decode('utf-8').splitlines()
