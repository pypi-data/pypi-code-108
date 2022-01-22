"""
tnnt template settings
"""

# Django
from django.conf import settings


def tnnt_settings(request):
    return_value = dict()

    # AA logo
    return_value["TNNT_TEMPLATE_AA_LOGO"] = "/static/icons/allianceauth.png"

    # entity ID
    # 1 if none is given
    try:
        return_value["TNNT_TEMPLATE_ENTITY_ID"] = settings.TNNT_TEMPLATE_ENTITY_ID
    except AttributeError:
        return_value["TNNT_TEMPLATE_ENTITY_ID"] = 1

    # entity type
    # 'alliance' if none is given
    try:
        return_value["TNNT_TEMPLATE_ENTITY_TYPE"] = settings.TNNT_TEMPLATE_ENTITY_TYPE
    except AttributeError:
        return_value["TNNT_TEMPLATE_ENTITY_TYPE"] = "alliance"

    # entity name
    # empty if none is given
    try:
        return_value["TNNT_TEMPLATE_ENTITY_NAME"] = settings.TNNT_TEMPLATE_ENTITY_NAME
    except AttributeError:
        return_value["TNNT_TEMPLATE_ENTITY_NAME"] = ""

    try:
        return_value[
            "TNNT_TEMPLATE_URLS_OWN_WEBSITES"
        ] = settings.TNNT_TEMPLATE_URLS_OWN_WEBSITES
    except AttributeError:
        pass

    try:
        return_value[
            "TNNT_TEMPLATE_URLS_OTHER_WEBSITES"
        ] = settings.TNNT_TEMPLATE_URLS_OTHER_WEBSITES
    except AttributeError:
        pass

    return return_value
