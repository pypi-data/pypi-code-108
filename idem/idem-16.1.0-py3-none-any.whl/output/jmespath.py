import pprint
from typing import Any
from typing import Dict
from typing import List


def display(hub, data):
    """
    Transform sls data into a format that is easily used in jmespath searches
    """
    return pprint.pformat(hub.output.jmespath.prepare(data))


def prepare(hub, data: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transform sls data into a format that is easily used in jmespath searches
    """
    if isinstance(data, List):
        # It's already in jmespath format
        return data
    ret = []
    if not data:
        return ret
    for sls_name, sls_data in data.items():
        for sls_ref, sls_params in sls_data.items():
            ret.append(
                {
                    "name": sls_name,
                    "ref": sls_ref,
                    "resource": sls_params,
                }
            )
    return ret


def revert(hub, obj: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """ "
    Transform jmespath data back into an sls style
    """
    ret = {}
    for item in obj:
        ret[item["name"]] = {item["ref"]: item["resource"]}
    return ret
