from psu_base.services import auth_service, utility_service, downtime_service
from psu_base.classes.Log import Log
from django.conf import settings
from datetime import datetime
from os import path

log = Log()


def auth(request):
    auth_object = auth_service.get_auth_object()
    logged_in = auth_service.is_logged_in()
    can_impersonate = auth_object.can_impersonate()
    can_proxy = auth_object.has_authority("proxy")
    is_impersonating = auth_object.is_impersonating()
    is_proxying = auth_object.is_proxying()
    # Cannot call a function from a template.  Pre-query for commonly-used roles
    is_developer = auth_service.has_authority("developer")
    is_sso_developer = auth_service.has_authority("developer", True)
    is_global_developer = auth_service.has_authority("developer", True, True)
    is_admin = auth_service.has_authority("admin")
    is_sso_admin = auth_service.has_authority("admin", True)
    is_global_admin = auth_service.has_authority("admin", True, True)
    is_power_user = auth_service.has_authority("~PowerUser")
    is_super_user = auth_service.has_authority("~SuperUser")
    return {
        "auth": auth_object,
        "current_user": auth_object.get_user(),
        "logged_in": logged_in,
        "not_logged_in": not logged_in,
        "can_impersonate": can_impersonate,
        "can_not_impersonate": not can_impersonate,
        "can_proxy": can_proxy,
        "can_not_proxy": not can_proxy,
        "is_impersonating": is_impersonating,
        "is_not_impersonating": not is_impersonating,
        "is_proxying": is_proxying,
        "is_not_proxying": not is_proxying,
        "is_developer": is_developer,
        "is_sso_developer": is_sso_developer,
        "is_global_developer": is_global_developer,
        "is_admin": is_admin,
        "is_sso_admin": is_sso_admin,
        "is_global_admin": is_global_admin,
        "is_power_user": is_power_user,
        "is_super_user": is_super_user,
    }


def util(request):
    # Build an absolute URL (for use in emails)
    absolute_root_url = "{0}://{1}".format(request.scheme, request.get_host())
    if "http://" in absolute_root_url and "localhost" not in absolute_root_url:
        absolute_root_url = absolute_root_url.replace("http://", "https://")

    model = {
        "now": datetime.now(),
        "absolute_root_url": absolute_root_url,
        # Check if local static files are available
        "use_local_static": settings.DEBUG or path.exists(settings.STATIC_ROOT),
        # The home URL (path) depends on existence of URL Context
        "home_url": f"/{settings.URL_CONTEXT}/" if settings.URL_CONTEXT else "/",
        "psu_plugins": utility_service.get_installed_plugins(),
        # Prod vs Nonprod
        "is_production": utility_service.is_production(),
        "is_non_production": utility_service.is_non_production(),
        "is_development": utility_service.is_development(),
        # Does PSU Logo color need to be modified (i.e. heading color is non-white)
        "modify_logo": settings.PSU_LOGO_FILTER is not None,
        "modify_logo_filter": settings.PSU_LOGO_FILTER.replace("filter:", "").strip(
            " ;"
        )
        if settings.PSU_LOGO_FILTER
        else None,
        "modify_logo_calculate": settings.PSU_LOGO_FILTER is None
        and settings.PRIMARY_FG_COLOR,
        # Flash messages at top of page by default. Setting option allows moving them to the bottom
        "flash_message_position": getattr(
            settings, "FLASH_MESSAGE_POSITION", "TOP"
        ).upper(),
        # Useful when there are sub-apps
        "app_code": utility_service.get_app_code(),
        "app_name": utility_service.get_app_name(),
    }

    # Downtime notices
    next_downtime = downtime_service.get_next_downtime()
    if next_downtime:
        model["active_downtime"] = next_downtime.is_active()
        model["next_downtime"] = next_downtime

    # Get admin links for any installed PSU plugins, and the current app
    plugin_admin_links = []
    apps = utility_service.get_installed_plugins()
    apps.update(
        {utility_service.get_app_code().lower(): utility_service.get_app_version()}
    )
    for plugin, version in apps.items():
        setting_name = f"{plugin.upper().replace('-', '_')}_ADMIN_LINKS"
        try:
            this_link_list = getattr(settings, setting_name)
            plugin_admin_links.extend(this_link_list)
        except AttributeError as ee:
            try:
                exec(f"from {plugin} import _DEFAULTS as {plugin}_defaults")
                these_links = eval(f"{plugin}_defaults['{setting_name}']")
                if these_links:
                    plugin_admin_links.extend(these_links)
            except Exception as ee:
                if plugin == utility_service.get_app_code().lower():
                    pass
                else:
                    log.debug(f"Error adding plugin links: {str(ee)}")

    model["plugin_admin_links"] = sorted(plugin_admin_links, key=lambda i: i["label"])

    # If white (the default color) was unnecessarily specified, logo doesn't need to be modified
    if model["modify_logo_calculate"]:
        if str(settings.PRIMARY_FG_COLOR).lower() in ["white", "#fff", "#ffffff"]:
            model["modify_logo_calculate"] = False
        elif settings.PRIMARY_FG_COLOR == (255, 255, 255):
            model["modify_logo_calculate"] = False
        elif settings.PRIMARY_FG_COLOR == (255, 255, 255, 1):
            model["modify_logo_calculate"] = False
        # If filter needs to be calculated, it also needs to be applied
        model["modify_logo"] = model["modify_logo_calculate"]

    return model
