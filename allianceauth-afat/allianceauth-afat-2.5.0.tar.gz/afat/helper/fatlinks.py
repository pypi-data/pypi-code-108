"""
Helper functions for fat links view
"""

# Standard Library
from typing import Dict, List, Union

# Alliance Auth
from allianceauth.authentication.admin import User

# Alliance Auth AFAT
from afat.models import AFatLink


def get_esi_fleet_information_by_user(
    user: User,
) -> Dict[str, Union[bool, List[Dict[int, AFatLink]]]]:
    """
    Get ESI fleet information by a given FC (user)
    :param user:
    :type user:
    :return:
    :rtype:
    """

    has_open_esi_fleets = False
    open_esi_fleets_list = list()
    open_esi_fleets = (
        AFatLink.objects.select_related_default()
        .filter(creator=user, is_esilink=True, is_registered_on_esi=True)
        .order_by("character__character_name")
    )

    if open_esi_fleets.count() > 0:
        has_open_esi_fleets = True

        for open_esi_fleet in open_esi_fleets:
            open_esi_fleets_list.append(open_esi_fleet)

    return {
        "has_open_esi_fleets": has_open_esi_fleets,
        "open_esi_fleets_list": open_esi_fleets_list,
    }
