from typing import Any
from typing import Dict

import dict_tools.data as data


async def profiles(
    hub,
    acct_file: str = None,
    acct_key: str = None,
) -> Dict[str, Any]:
    """
    Read the acct information from the named subs and return the context
    """
    if acct_file and acct_key:
        hub.log.debug("Reading profiles from acct")
        all_profiles = await hub.acct.init.profiles(acct_file, acct_key)
    else:
        all_profiles = {}

    ret_profiles = data.NamespaceDict()

    subs = set()
    for provider, profile in all_profiles.items():
        ret_profiles[provider] = {}
        for name, info in profile.items():
            if provider in hub.acct:
                # This profile might need additional processing
                subs.add(provider)
            ret_profiles[provider][name] = info

    # Create sub profiles
    new_profiles = await hub.acct.init.process(subs, ret_profiles)
    ret_profiles.update(new_profiles)

    return ret_profiles
