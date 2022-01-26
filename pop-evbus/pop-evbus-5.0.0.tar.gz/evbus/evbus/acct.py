from typing import Any
from typing import Dict
from typing import List

import dict_tools.data as data


async def profiles(
    hub,
    acct_file: str = None,
    acct_key: str = None,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Read the acct information from the named subs and return the context
    """
    if acct_file and acct_key:
        hub.log.debug("Reading profiles from acct")
        acct_data = await hub.acct.init.profiles(acct_file, acct_key)
    else:
        acct_data = {}

    ret_data = data.NamespaceDict()

    for provider, profiles in acct_data.items():
        ret_data[provider] = []
        if not isinstance(profiles, list):
            profiles = [profiles]
        for profile in profiles:
            for name, info in profile.items():
                ret_data[provider].append(data.NamespaceDict({name: info}))
                if provider in hub.acct:
                    # This profile needs to run through an acct plugin for processing
                    new_info = await hub.acct.init.process(
                        {provider}, {provider: {name: info}}
                    )
                    ret_data[provider].append(data.NamespaceDict({name: new_info}))

    return ret_data
