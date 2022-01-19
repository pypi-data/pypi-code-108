from django.conf import settings
from django.db.models import Q
from psu_base.services import error_service, validation_service
from psu_base.classes.Log import Log
from psu_base.models import Feature, FeatureToggle, AdminScript
from crequest.middleware import CrequestMiddleware
from psu_base.classes.Finti import Finti
from psu_base.classes.ConvenientDate import ConvenientDate
from inspect import getframeinfo, stack, getmembers
from collections import OrderedDict
import re
import os
import hashlib
import requests
import base64
import sys

log = Log()
unit_test_session = {"modified": False, "warned": False}


def get_setting(property_name, default_value=None):
    """
    Get the value of a setting from settings, psu_settings, app_settings, or local_settings
    """
    return (
        getattr(settings, property_name)
        if hasattr(settings, property_name)
        else default_value
    )


def get_app_code():
    """
    Get the app code of the current application
    The app code is used to specify the current app in shared psu_base tables
    The app code is also used for determining permissions
    """
    app_code = recall()
    if app_code:
        return app_code

    primary_app_code = app_in_use = get_setting("APP_CODE").upper()

    # Starting with v 3.0.0, an app can have multiple sub-apps
    sub_apps = get_setting("SUB_APPS")
    if sub_apps:
        # Info about sub app usage is stored in session
        sub_app_info = get_sub_app_info(primary_app_code)
        last_app = sub_app_info["current_app"]

        # By convention, sub-app paths must start with the sub-app code
        request = get_request()
        path = request.path if request else "/"
        pieces = [x for x in path.split("/") if x]
        # If there is URL context, sub-app code will be after the context
        sub_app_index = 1 if get_setting("URL_CONTEXT") else 0
        # Get potential sub-app code
        sub_app_code = (
            pieces[sub_app_index].upper() if len(pieces) > sub_app_index else None
        )

        # Is the potential sub-app code a defined sub-app?
        if sub_app_code and sub_app_code in sub_apps:
            app_in_use = sub_app_code

        # Is the potential sub-app code the primary app?
        elif sub_app_code and sub_app_code == primary_app_code:
            app_in_use = primary_app_code

        # Otherwise, use the last-known APP_CODE
        elif last_app:
            # Sub-app code persists into generic (psu) pages until a new sub-app is visited
            app_in_use = last_app
        # If no previous app is known, use the primary APP_CODE
        else:
            app_in_use = primary_app_code

        # Update session app info
        app_changed = app_in_use != last_app
        if app_changed:
            log.trace(f"SUB-APP CHANGED from {last_app} to {app_in_use}")
        is_sub_app = app_in_use != primary_app_code
        sub_app_info = {
            "last_app": last_app,
            "current_app": app_in_use,
            "is_sub_app": is_sub_app,
            "app_changed": app_changed,
        }
        set_sub_app_info(sub_app_info)

    return store(app_in_use)


def get_sub_app_info(primary_app_code=None):
    sub_app_info = {
        "last_app": primary_app_code,
        "current_app": None,
        "is_sub_app": None,
        "app_changed": False,
    }
    return get_session_var("SUB_APP_INFO", sub_app_info)


def set_sub_app_info(sub_app_info):
    set_session_var("SUB_APP_INFO", sub_app_info)


def get_app_name():
    """
    Get the human-readable name of the current application
    This is mainly used in administrative views
    """
    sub_apps = get_setting("SUB_APPS")
    if sub_apps:
        app_code = get_app_code()
        if app_code in sub_apps:
            return sub_apps[app_code]
    return get_setting("APP_NAME")


def get_app_version():
    """
    Get the human-readable name of the current application
    This is mainly used in administrative views
    """
    return get_setting("APP_VERSION")


def get_installed_plugins():
    """
    Get a dict of the installed PSU plugins and their versions
    """
    installed_apps = {}
    for app_name in get_setting("INSTALLED_APPS"):
        if app_name.startswith("psu"):
            version = "?.?.?"
            try:
                for stuff in getmembers(sys.modules[f"{app_name}"]):
                    if "__version__" in stuff:
                        version = stuff[1]
            except Exception as ee:
                log.debug(f"Cannot determine version of {app_name}")
            installed_apps[app_name] = version

    return installed_apps


def get_environment():
    """
    Get environment: DEV, STAGE, PROD (TEST is no longer an option)
    """
    env = settings.ENVIRONMENT.upper()
    if env in ["DEV", "STAGE", "PROD"]:
        return env
    elif env in ["OPRD", "PRODUCTION"]:
        return "PROD"
    elif env in ["TEST"]:
        log.warning(
            "Environment is defined as TEST, which is no longer an option. Using STAGE instead."
        )
        return "STAGE"
    else:
        return "DEV"


def is_production():
    return get_environment() == "PROD"


def is_non_production():
    return get_environment() != "PROD"


def is_development():
    return (get_environment() == "DEV") and settings.DEBUG


def is_health_check():
    browser = get_browser()
    return "HealthChecker" in browser


def is_ajax():
    # request.is_ajax was deprecated in Django 3.1 and no longer exists in 3.2.10
    return get_request().headers.get('x-requested-with') == 'XMLHttpRequest'


def get_static_content_url():
    """Get the appropriate Static Content URL for the current environment"""
    if is_production():
        return settings.CENTRALIZED_PROD
    else:
        return settings.CENTRALIZED_NONPROD


def get_request():
    return CrequestMiddleware.get_request()


def get_parameters():
    """Get parameters as dict. This is mostly for logging parameters."""
    request = get_request()
    if request:
        pp = request.GET.items() if request.method == "GET" else request.POST.items()
        return {kk: vv for kk, vv in pp}
    return None


def get_browser():
    try:
        request = get_request()
        browser = request.META["HTTP_USER_AGENT"]
    except:
        browser = "Unknown"
    return browser


def pagination_sort_info(
    request,
    default_sort="id",
    default_order="asc",
    filter_name=None,
    reset_page=False,
    sort_tuple=True,
):
    """
    Get the pagination sort order and page info.
    Sort info, page number, and filters are automatically tracked in the session.

    Parameters:
        request:        Django 'request' object (from view)
        default_sort:   Property/Column to sort by
        default_order:  asc or desc
        filter_name:    If view is filtering on a keyword string, or list of keyword strings, maintain that here as well
        reset_page:     True will force back to page 1 (i.e. new search/filter terms submitted)
        sort_tuple:     Return tuple rather than string as sort parameter. Allows multiple sort columns.
    Returns tuple: (sortby-string-or-tuple, page-number)
        sortby-string includes column and direction ('id', '-id')
        page-number is recommended page number (reset to 1 after sort change)

        if filter_name was given, tuple will have a third item:
            - if filter_name is a single item: a single string will be returned
            - if filter_name is a list of names, a dict of {name: value} will be returned
    """

    # Make sure filter name is a list (with 0, 1, or more items)
    if not filter_name:
        filter_name_list = []
    elif type(filter_name) is list:
        filter_name_list = filter_name
    else:
        filter_name_list = [filter_name]

    fn = _get_cache_key()
    sort_var = f"{fn}-sort"
    order_var = f"{fn}-order"
    page_var = f"{fn}-page"
    filter_vars = {}
    for ff in filter_name_list:
        filter_vars[ff] = f"{fn}-filter-{ff}"

    # Get default sort, order, filter, page
    default_sort = get_session_var(sort_var, default_sort)
    default_order = get_session_var(order_var, default_order)
    default_page = get_session_var(page_var, 1)

    default_filters = {}
    for ff in filter_name_list:
        default_filters[ff] = get_session_var(filter_vars[ff], None)

    # Make default sort a tuple
    if type(default_sort) in [tuple, list]:
        default_sort = tuple(default_sort)
    elif default_sort:
        default_sort = (default_sort,)

    # Get values from parameters
    specified_sort = request.GET.get("sort", None)
    if specified_sort and "," in specified_sort:
        specified_sort = csv_to_list(specified_sort)
    specified_order = request.GET.get("order", None)
    page = request.GET.get("page", default_page)

    specified_filters = {}
    for ff in filter_name_list:
        if ff in request.GET:
            # Get parameter as a list
            as_list = request.GET.getlist(ff, None)

            # If filter is named with "list" then treat it as a list even if it has 0 or 1 value
            if "list" in ff:
                specified_filters[ff] = as_list
            # If not named as a list, but multiple values are present, return as a list
            elif as_list and len(as_list) > 1:
                specified_filters[ff] = as_list
            # Otherwise, return single value
            else:
                specified_filters[ff] = request.GET.get(ff, None)

        else:
            specified_filters[ff] = default_filters.get(ff)

    # Did the sort column change?
    if not specified_sort:
        sort_changed = False
    elif type(specified_sort) is list:
        sort_changed = specified_sort[0] and specified_sort[0] != default_sort[0]
        if len(specified_sort) > 1 and not sort_changed:
            if len(default_sort) < 2:
                sort_changed = True
            else:
                sort_changed = (
                    specified_sort[1] and specified_sort[1] != default_sort[1]
                )
    else:
        sort_changed = specified_sort and specified_sort != default_sort[0]

    filter_changed = False
    for ff in filter_name_list:
        if ff in request.GET and specified_filters[ff] != default_filters[ff]:
            filter_changed = True

    # If sort is specified, adjust order as needed and return to page 1
    if specified_sort:
        page = 1

        # If sort has changed
        if sort_changed:
            # default to ascending order
            order = "asc"

            # make secondary sort by the previous selection
            try:
                if type(specified_sort) is list:
                    sort = tuple(specified_sort)
                else:
                    sort = (specified_sort,)

                if default_sort:
                    sort = sort + (default_sort[0],)

            except Exception as ee:
                error_service.record(ee, f"Error updating default sort: {default_sort}")
                sort = (specified_sort,)

        # If sort has not changed
        elif specified_order:
            sort = default_sort
            order = specified_order

        # If sort stayed the same toggle between asc and desc
        else:
            sort = default_sort
            order = "asc" if default_order == "desc" else "desc"

    # If sort not specified, use default
    else:
        sort = default_sort
        order = default_order

    # If filter string changed, page will need to be reset
    if filter_changed:
        filter_strings = specified_filters
        page = 1
    else:
        filter_strings = default_filters

    if reset_page:
        page = 1

    # Remember sort preference
    set_session_var(sort_var, sort)
    set_session_var(order_var, order)
    set_session_var(page_var, page)
    for ff in filter_name_list:
        set_session_var(filter_vars[ff], filter_strings[ff])

    # Sortable column header taglib needs to know the last-sorted column
    # This assumes only one sorted dataset is being displayed at a time
    set_session_var(
        "psu_last_secondary_sorted_column",
        sort[1] if type(sort) is tuple and len(sort) > 1 else sort,
    )
    set_session_var("psu_last_sorted_column", sort[0] if type(sort) is tuple else sort)
    set_session_var("psu_last_sorted_direction", order)

    oo = "-" if order == "desc" else ""
    if type(sort) is tuple:
        sort_param = ()
        for vv in sort:
            sort_param += (f"{oo}{vv}",)

    elif sort:
        sort_param = (f"{oo}{sort}",)

    else:
        sort_param = None

    # If tuple not being used for sort param
    if not sort_tuple:
        sort_param = sort_param[0] if sort_param else None

    if filter_name:
        if len(filter_strings) == 1:
            return_val = sort_param, page, filter_strings[filter_name]
        else:
            return_val = sort_param, page, filter_strings
    else:
        return_val = sort_param, page

    return return_val


def get_session():
    # While unit testing, there will be no request
    request = get_request()

    if request is None:
        # This should not happen in prod, but just to be sure
        if is_production():
            log.error("Request does not exist. Could not retrieve session.")
            return None
        else:
            # Only warn about this once (to prevent cluttered logs)
            if not unit_test_session.get("warned"):
                log.warning("No request. Using dict as session (assumed unit testing)")
                unit_test_session["warned"] = True
            return unit_test_session
    else:
        return request.session


def set_session_var(var, val):
    session = get_session()
    session[var] = val
    return val


def get_session_var(var, alt=None):
    session = get_session()
    return session.get(var, alt)


def set_temp_session(var, val):
    log.warning(
        "DEPRECATED: utility_service.set_temp_session() -- Use set_page_scope() instead"
    )
    set_page_scope(var, val)
    return val


def get_temp_session(var, alt=None):
    log.warning(
        "DEPRECATED: utility_service.get_temp_session() -- Use get_page_scope() instead"
    )
    return get_page_scope(var, alt)


def set_page_scope(var, val):
    var_name = f"page_scope_{var}"
    set_session_var(var_name, val)
    return val


def get_page_scope(var, alt=None):
    var_name = f"page_scope_{var}"
    return get_session_var(var_name, alt)


def set_flash_variable(var, val):
    var_name = f"flash_scope_{var}"
    set_session_var(var_name, val)
    return val


def get_flash_variable(var, alt=None):
    # Get the value saved in previous request
    prev_var_name = f"flashed_scope_{var}"
    previous_flash_value = get_session_var(prev_var_name, alt)

    # Get new value if overwritten during the current request
    new_var_name = f"flash_scope_{var}"
    new_flash_value = get_session_var(new_var_name, "flash-variable-not-set")

    # return the more recent of the two
    # (flash variable from last request can be overwritten this request)
    if new_flash_value != "flash-variable-not-set":
        return new_flash_value
    else:
        return previous_flash_value


def cycle_flash_scope():
    session = get_session()
    flash_vars = []
    flashed_vars = []
    for kk in session.keys():
        if kk.startswith("flash_scope_"):
            flash_vars.append(kk)
        elif kk.startswith("flashed_scope_"):
            flashed_vars.append(kk)
    # Remove the keys from the flashed scope
    for kk in flashed_vars:
        del session[kk]
    # Move flash vars to flashed scope
    for kk in flash_vars:
        new_kk = kk.replace("flash_", "flashed_")
        session[new_kk] = session[kk]
        del session[kk]

    session["modified"] = True


def store(value):
    """
    Store the result of a function for the duration of the request.
    Note: If the stored response is mutable, changes made to the returned value will affect the cached instance as well
    """
    set_page_scope(_get_cache_key(), value)
    return value


def recall():
    """
    Retrieve a stored result from a function run earlier in the request
    Note: If the stored response is mutable, changes made to the returned value will affect the cached instance as well
    """
    return get_page_scope(_get_cache_key())


def _get_cache_key():
    """
    Private function
    Get the key used by store/recall functions above
    UPDATE: This is also used for remembering pagination sort/order
    """
    # Ignore this function, and the store/recall function that called it
    depth = 2

    # Get the info about the function that called the store/recall function
    caller = getframeinfo(stack()[depth][0])

    # Use filename without .py extension
    filename = os.path.basename(caller.filename)[:-3]

    return f"cache-{filename}-{caller.function}"


def test_cache_key():
    """
    The only purpose of this function is to unit test the "cache key" generated above
    """
    return _get_cache_key()


def test_store_recall(value=None):
    """
    The only purpose of this function is to unit test the store/recall feature
    """
    if value:
        store(value)
    else:
        return recall()


def clear_page_scope():
    session = get_session()
    temp_vars = []
    for kk in session.keys():
        if kk.startswith("page_scope_"):
            temp_vars.append(kk)
    # Remove the keys from the session
    for kk in temp_vars:
        del session[kk]

    session["modified"] = True


def append_session_log(message):
    session_log = get_session_log()
    session_log.append(message)
    set_page_scope("session_log", session_log)


def get_session_log():
    session_log = []
    return get_page_scope("session_log", session_log)


def csv_to_list(src, convert_int=False):
    """Turn a string of comma-separated values into a python list"""
    result_list = None

    # If a list was already given, no conversion needed
    if type(src) is list or type(src) is None:
        result_list = src

    elif src == "":
        return None

    else:
        # Make sure we're working with a string
        src = str(src)

        # If the string "None" was given, return None
        if src == "None":
            return None

        # Often, this is a python list that has been converted to a string at some point
        if src[0] == "[" and src[-1] == "]":
            src = src[1:-1]  # Remove brackets

        result_list = [
            ii.strip("\"' ") if type(ii) is str else ii for ii in src.split(",") if ii
        ]

    # If converting list elements to a specified type
    if convert_int:
        return [int(ii) if type(ii) is str else ii for ii in result_list]
    # elif convert_<future-type>:
    #    return ...
    else:
        return result_list


def options_list_to_dict(options):
    """
    Finti returns options from validation tables as a list of dicts.
    This function converts the list of dicts to a single dict of options
    """
    # Expecting a list of {id:, value:} dicts
    # A list of {key:, value:} dicts will also work
    if type(options) is list:
        # Convert the list to one big dict
        option_dict = OrderedDict()
        for ii in options:
            option_dict[ii["id" if "id" in ii else "key"]] = ii["value"]
        return option_dict
    elif type(options) is dict:
        return options
    else:
        error_service.record(
            "Invalid datatype for options",
            "Expecting list of {0}. Got {1}".format(
                "{id:, value:} dicts", type(options)
            ),
        )


def contains_script(value):
    """Does the given value appear to contain a script tag (generic XSS checking)?"""

    # Empty values cannot have scripts
    if value is None:
        return False

    # Get value as a string and strip whitespace for comparisons
    string_value = str(value).strip()

    # Empty strings cannot have scripts
    if value == "":
        return False

    # Look for an obvious script tag
    script_tag = r"<\s?script"

    # Look for a src="javascript:..." tag
    script_src = r'<.*src\s?=\s?[\'"].*script.+'

    # Look for an on* event
    script_evt = r'<.*on\w+\s?=\s?[\'"].*'

    # Look for an iframe tag
    iframe_tag = r"<\s?iframe"

    if re.search(script_tag, string_value, re.I):
        return True
    if re.search(script_src, string_value, re.I):
        return True
    if re.search(script_evt, string_value, re.I):
        return True
    if re.search(iframe_tag, string_value, re.I):
        return True

    return False


def get_banweb_url():
    return Finti(suppress_logging=True).get("wdt/v1/sso_proxy/public/banweb_url")


# ===                 ===
# === FEATURE TOGGLES ===
# ===                 ===


def feature_is_enabled(feature_code):
    """
    Is the given feature code active for this app?
    """
    feature = get_feature(feature_code)

    # If feature was not found, create it
    if feature is None:
        log.info(f"Creating feature: {feature_code}")
        # For apps with multiple sub-apps, create as a global default
        if get_setting("SUB_APPS"):
            app_code = None
            default = "Y"
        else:
            app_code = get_app_code()
            default = "N"
        feature = Feature(
            app_code=app_code,
            default=default,
            feature_code=feature_code,
            feature_title=f"Feature: {feature_code}",
            status="N",  # New features will default to inactive
        )
        feature.save()
        set_page_scope(
            "features", None
        )  # Force re-query of features to prevent duplicate feature inserts

    # If feature is limited to admins (for testing/validation of new feature)
    if feature.status == "L":
        # Is this an admin/developer with access to Limited features?
        return get_session_var("allow_limited_features")

    else:
        return feature.status == "Y"


def get_feature(feature_code):
    return get_features().get(feature_code)


def get_features():
    """"""
    # Retrieve from temp session, if exists
    results = get_page_scope("features")
    if not results:
        # If not cached, query for the features
        results = {}

        # Get all app and global features and then select the correct ones (accounting for defaults and overrides)
        features = Feature.objects.filter(
            Q(app_code=get_app_code()) | Q(app_code__isnull=True)
        )

        # Sort by feature_code
        if features:
            feature_dict = {}
            for ff in features:
                # Initialize the dict, if needed
                if ff.feature_code not in feature_dict:
                    feature_dict[ff.feature_code] = {
                        "app": None,
                        "default": None,
                        "override": None,
                    }
                # Sort by app, default, or override
                if ff.app_code == get_app_code():
                    feature_dict[ff.feature_code]["app"] = ff
                elif ff.override == "Y":
                    feature_dict[ff.feature_code]["override"] = ff
                else:
                    feature_dict[ff.feature_code]["default"] = ff

            # Select the appropriate instance of each feature
            now = ConvenientDate("now")
            for feature_code, ff in feature_dict.items():
                selected = (
                    ff["override"]
                    if ff["override"]
                    else ff["app"]
                    if ff["app"]
                    else ff["default"]
                )

                # Update status based on start/end dates, if applicable
                if selected.enable_date:
                    try:
                        start = ConvenientDate(selected.enable_date_display())
                        if start.datetime_instance <= now.datetime_instance:
                            selected.status = "Y"
                            selected.enable_date = None
                            selected.save()
                    except Exception as ee:
                        error_service.unexpected_error(None, ee)

                if selected.status != "N" and selected.disable_date:
                    try:
                        end = ConvenientDate(selected.disable_date_display())
                        if end.datetime_instance <= now.datetime_instance:
                            selected.status = "N"
                            selected.disable_date = None
                            selected.save()
                    except Exception as ee:
                        error_service.unexpected_error(None, ee)

                results[feature_code] = selected.to_dict()

            # Cache the results
            set_page_scope("features", results)
            del features
            del feature_dict

    # Convert cached results into FeatureToggle classes
    feature_toggles = {}
    if results:
        for feature_code, ff in results.items():
            feature_toggles[feature_code] = FeatureToggle(ff)
        del results

    return feature_toggles


def get_gravatar_image_src(email_address):
    """
    PSU ID photos are used for the authenticated user, but are not necessarily recent.
    If the user took the time to set up a Gravatar image, it will be used instead of the ID Photo.
    """
    if get_setting("DISABLE_GRAVATAR"):
        return None

    if not email_address:
        return None

    log.trace([email_address])
    try:
        email = email_address.strip().lower()
        m = hashlib.md5()
        m.update(email.encode())
        email_hash = m.hexdigest()

        # Provide an alt image so that a consistent response can indicate not having a Gravatar image
        alt_img = f"{get_static_content_url()}/images/no-id-photo.png"
        url = f"https://www.gravatar.com/avatar/{email_hash}?s=200&d={alt_img}"

        # Get the image data
        b64img = base64.b64encode(requests.get(url).content).decode()

        # If this is the default image, return None
        if b64img.startswith(
            "iVBORw0KGgoAAAANSUhEUgAAAQAAAAEACAMAAABrrFhUAAAAM1BMVEXn6+7g5em4xMvFz9XM1drk6Oy/ydCxvsa0wcn"
        ):
            return None

        return """data:image/jpg;base64,{0}""".format(b64img)

    except Exception as ee:
        log.error(f"Error getting Gravatar image: {str(ee)}")
        return None


def get_admin_scripts(request, username):
    scripts = AdminScript.objects.filter(
        Q(app_code=get_app_code()) | Q(app_code__isnull=True)
    )
    applicable_scripts = []
    for ss in scripts:
        if not ss.is_active():
            continue
        if ss.target_username and ss.target_username != username:
            continue
        if ss.target_url and ss.target_url not in request.path:
            continue
        applicable_scripts.append(ss)

    del scripts
    return applicable_scripts


def format_phone(phone_number, no_special_chars=False):
    """
    Format a phone number.
    """
    src = initial_string = str(phone_number) if phone_number else ""
    if " ext " in initial_string:
        src = initial_string.replace(" ext ", "")
    word_chars_only = re.sub(r"\W", "", src).upper()
    digits_only = re.sub(r"\D", "", src)

    # Remove unnecessary country code
    if len(digits_only) == 11 and digits_only.startswith("1"):
        digits_only = digits_only[1:]

    # Maybe it's an abbreviated campus number
    elif len(digits_only) == 5 and digits_only.startswith("5"):
        digits_only = "50372{}".format(digits_only)
    elif len(digits_only) == 7 and digits_only.startswith("725"):
        digits_only = "503{}".format(digits_only)

    # If a clean 10-digit number was given, split into the standard pieces
    # If longer than 10 digits, assume extra to be an extension
    if len(digits_only) > 10:
        if no_special_chars:
            return digits_only
        else:
            return f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:10]} ext {digits_only[10:]}"
    elif len(digits_only) == 10:
        if no_special_chars:
            return digits_only
        else:
            return f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:10]}"

    # If too short, just return it as-is. Maybe a real live human will figure it out.
    else:
        # If only 7-digits, return as a phone number with no area code
        if no_special_chars:
            return word_chars_only
        elif len(word_chars_only) == 7:
            return f"{word_chars_only[:3]}-{word_chars_only[3:]}"
        else:
            return initial_string.upper()


def term_description(term_code):
    if term_code and len(term_code) == 6:
        year = term_code[:4]
        term = term_code[4:]
        if term == "01":
            season = "Winter"
        elif term == "02":
            season = "Spring"
        elif term == "03":
            season = "Summer"
        elif term == "04":
            season = "Fall"
        else:
            return term_code

        return f"{season} {year}"

    elif term_code:
        log.warning(f"Could not get description from invalid term code: {term_code}")

    return term_code


def is_term(string):
    """Is the given string a term code?"""
    if is_non_production():
        log.warning(
            "DEPRECATED: utility_service.is_term() has moved to validation_service"
        )
    return validation_service.is_term(string)


def is_psu_id(string):
    """Is the given string (likely) a PSU ID?"""
    if is_non_production():
        log.warning(
            "DEPRECATED: utility_service.is_psu_id() has moved to validation_service"
        )
    return validation_service.is_psu_id(string)


def has_unlikely_characters(value, unlikely_characters="`!*=\\$%^[]{}<>;"):
    if is_non_production():
        log.warning(
            "DEPRECATED: utility_service.has_unlikely_characters() has moved to validation_service"
        )
    return validation_service.has_unlikely_characters(value, unlikely_characters)


def decamelize(string):
    """Convert CamelCaseWord to camel_case_word"""
    result = ""
    ii = 0
    for xx in string:
        # if this is an upper case letter, add an underscore
        if xx != xx.lower() and ii != 0:
            result += "_"

        result += xx.lower()
        ii += 1

    return result


def camelize(string, cap_first_letter=False):
    """Convert camel_case_word to camelCaseWord"""
    result = ""
    ii = 0
    cap_next_letter = cap_first_letter
    for xx in string:

        # if this is an underscore, capitalize next letter
        if xx == "_":
            cap_next_letter = True
            continue

        if cap_next_letter:
            result += xx.upper()
        else:
            result += xx.lower()

        cap_next_letter = False
        ii += 1

    return result


def to_choices(options):
    """
    Convert a dictionary or list of dictionaries to a list of tuples as expected by Django's choice fields
    """
    if isinstance(options, dict):
        return list(options.items())
    elif options and isinstance(options[0], dict):
        return [(i.get("id") or i.get("key"), i["value"]) for i in options]
    return options
