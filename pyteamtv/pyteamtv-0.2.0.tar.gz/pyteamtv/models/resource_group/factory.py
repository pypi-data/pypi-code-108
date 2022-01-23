from pyteamtv.infra.requester import Requester
from .person import PersonResourceGroup
from .team import TeamResourceGroup
from .club import ClubResourceGroup
from .sharing_group import SharingGroupResourceGroup
from .reseller import ResellerResourceGroup
from .exchange import ExchangeResourceGroup
from .app_developer import AppDeveloperResourceGroup
from .user import UserResourceGroup


def factory(requester: Requester, attributes: dict):
    """

    :param requester:
    :param attributes:
    :rtype: Team
    """
    _CLASSES = {
        'team': TeamResourceGroup,
        'club': ClubResourceGroup,
        'SharingGroup': SharingGroupResourceGroup,
        'reseller': ResellerResourceGroup,
        'exchange': ExchangeResourceGroup,
        'app-developer': AppDeveloperResourceGroup,
        'user': UserResourceGroup,
        'person': PersonResourceGroup
    }

    target_resource_type, target_resource_id = attributes['targetResourceId'].split(":")

    if target_resource_type not in _CLASSES:
        raise Exception(f"Unknown resource group type {target_resource_type}")

    return _CLASSES[target_resource_type](
        requester.with_extra_headers({
            'X-Resource-Group-Id': attributes['resourceGroupId']
        }),
        attributes
    )
