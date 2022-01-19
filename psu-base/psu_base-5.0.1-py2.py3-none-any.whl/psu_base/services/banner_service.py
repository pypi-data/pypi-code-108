from psu_base.services import error_service, utility_service
from django.http import JsonResponse
from psu_base.classes.Log import Log
from psu_base.classes.Finti import Finti

log = Log()
unit_test_session = {"modified": False, "warned": False}


def finti_get_json_response(path, parameters=None, include_metadata=False):
    """
    Make a GET request and return the result as a JsonResponse with appropriate HTTP status code
    """
    finti = Finti()
    response = JsonResponse(
        Finti().get(path=path, parameters=parameters, include_metadata=include_metadata)
    )
    response.status_code = finti.http_status_code
    return response


def finti_post_json_response(
    path, payload=None, headers=None, include_metadata=False, json_payload=None
):
    """
    Make a POST request and return the result as a JsonResponse with appropriate HTTP status code
    """
    finti = Finti()
    response = JsonResponse(
        Finti().post(
            path,
            payload=payload,
            headers=headers,
            include_metadata=include_metadata,
            json_payload=json_payload,
        )
    )
    response.status_code = finti.http_status_code
    return response


def finti_get_menu_options_response(menu_type):
    """
    Get menu options from Banner validation tables as a JsonResponse with appropriate HTTP status code
    """
    finti = Finti()
    response = JsonResponse(finti_get_menu_options(menu_type, finti))
    response.status_code = finti.http_status_code
    return response


def finti_get_menu_options(menu_type, finti_instance=None):
    """
    Get menu options from Banner validation tables.
    Examples of menu_type include state, nation, race, ethnicity, ...
    The complete list of available menu_types is only found in Banner: api/dbprocs/zwd_form_options
    """
    log.trace([menu_type])

    # Get a new Finti instance if not provided
    # (Instance might be provided for error/status tracking from the calling function)
    if finti_instance is None:
        finti_instance = Finti()

    # Get the menu options
    options = finti_instance.get(f"wdt/v1/menu_options/{menu_type}")

    # If options were not found, log the error message and return an empty dict
    if not finti_instance.successful:
        log.error(options)
        return {}

    # Otherwise, return the options as a dict
    else:
        return utility_service.options_list_to_dict(options)
