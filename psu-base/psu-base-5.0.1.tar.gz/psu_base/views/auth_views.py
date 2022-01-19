from django.shortcuts import redirect, render
from psu_base.classes.Log import Log
from psu_base.services import auth_service, utility_service
from django.views.decorators.csrf import csrf_protect
from psu_base.decorators import (
    require_impersonation_authority,
    require_authority,
    require_authentication,
)
from psu_base.classes.User import User

log = Log()


@require_impersonation_authority()
def stop_impersonating(request):
    """
    To stop impersonating, the session will be cleared.
    Therefore, any proxy selected while impersonating will also be removed.
    """
    return partial_logout(
        request,
        next_destination=request.GET.get("next", request.META.get("HTTP_REFERER")),
    )


@require_authority("proxy")
def stop_proxying(request):
    """
    To stop proxying, the session will be cleared.
    If user is also impersonating, that can be resumed as a new impersonation.
    """
    auth_object = auth_service.get_auth_object()
    if auth_object.is_impersonating():
        impersonate_user = auth_object.impersonated_user.username
    else:
        impersonate_user = None

    return partial_logout(
        request,
        next_impersonation=impersonate_user,
        next_destination=request.GET.get("next", request.META.get("HTTP_REFERER")),
    )


@csrf_protect
@require_impersonation_authority()
def start_impersonating(request):
    """
    Handle the impersonation form and redirect to home page
    """
    impersonation_data = request.POST.get("impersonation_data")
    return partial_logout(
        request,
        next_impersonation=impersonation_data,
        next_proxy=None,
        next_destination=request.POST.get("next", request.META.get("HTTP_REFERER")),
    )


@csrf_protect
@require_authority("proxy")
def start_proxying(request):
    """
    Handle the proxy user form and redirect to home page
    """
    auth_object = auth_service.get_auth_object()
    if auth_object.is_impersonating():
        impersonate_user = auth_object.impersonated_user.username
    else:
        impersonate_user = None

    proxy_data = request.POST.get("proxy_data")

    return partial_logout(
        request,
        next_impersonation=impersonate_user,
        next_proxy=proxy_data,
        next_destination=request.POST.get("next", request.META.get("HTTP_REFERER")),
    )


def partial_logout(
    request, next_impersonation=None, next_proxy=None, next_destination="/"
):
    # Clear all session (and authentication) data (except sub-app info)
    sai = utility_service.get_sub_app_info()
    log.info("Clearing session for requested authentication change")
    request.session.clear()
    utility_service.set_sub_app_info(sai)

    # Remember what to do next
    request.session["next_impersonation"] = next_impersonation
    request.session["next_proxy"] = next_proxy
    request.session["next_destination"] = next_destination

    # Redirect (to retrieve CAS attributes)
    return redirect("psu:initiate_auth")


@require_authentication()
def initiate_auth(request):
    """
    Instructions are stored in the session by partial_logout()
    """
    # Flag to indicate if user needs to search again (invalid proxy selection)
    search_for_proxy = False

    # Retrieve instructions from session
    next_impersonation = request.session.get("next_impersonation")
    next_proxy = request.session.get("next_proxy")
    next_destination = request.session.get("next_destination", "/")

    # Remove instructions from session
    del request.session["next_impersonation"]
    del request.session["next_proxy"]

    # If initiating/resuming an impersonation
    auth = auth_service.get_auth_object()
    if next_impersonation and auth.can_impersonate():
        success = auth.start_impersonating(next_impersonation)
        if success:
            # Audit successful impersonation selections
            auth_service.audit_event("impersonation")
            utility_service.set_flash_variable("new_impersonation", True)
        else:
            search_for_proxy = True
            next_destination = "psu:proxy_search"

    # If initiating a proxy
    auth = auth_service.get_auth_object()
    if next_proxy and auth.has_authority("proxy"):
        success = auth.set_proxy(next_proxy)
        if success:
            # Audit successful proxy selections
            auth_service.audit_event("proxy_selection")
        else:
            search_for_proxy = True
            next_destination = "psu:proxy_search"

    # If not searching for new proxy, remove the next destination from session
    if not search_for_proxy:
        del request.session["next_destination"]

    try:
        return redirect(next_destination)
    except:
        # If next destination was not valid, go to root instead
        return redirect("/")


@require_authority(["~impersonate", "proxy"])
def proxy_search(request):
    """
    When a proxy attempt fails, offer a user search screen
    """
    found = None

    if request.method == "POST" and request.POST.get("proxy_info"):
        pass

    elif request.method == "POST" and request.POST.get("search_info"):
        # Look up user from given data
        found = User(request.POST.get("search_info"))

    return render(request, "auth/proxy_search.html", {
        "found": found,
        "next": request.session.get("next_destination", "/")
    })
