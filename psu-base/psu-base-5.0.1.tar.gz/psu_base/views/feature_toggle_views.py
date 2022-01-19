# testing_views.py
#
#   These are views that are used for debugging or testing the status of an app
#

from django.shortcuts import render
from django.shortcuts import redirect
from psu_base.services import utility_service, auth_service, message_service
from psu_base.decorators import require_authority
from psu_base.models.feature import Feature
from django.http import (
    HttpResponseNotAllowed,
    Http404,
    HttpResponseForbidden,
    HttpResponse,
)
import re
from psu_base.classes.Log import Log
from psu_base.classes.ConvenientDate import ConvenientDate

log = Log()
allowable_role_list = ["~super_user", "features"]


@require_authority(allowable_role_list)
def feature_list(request):
    """
    List all features for this application
    """
    # Can the user manage features for ALL apps?
    is_global_admin = auth_service.has_authority(
        allowable_role_list, require_global=True
    )

    # Get all features (app and globals)
    app_features = Feature.objects.filter(app_code=utility_service.get_app_code())
    global_overrides = Feature.objects.filter(app_code__isnull=True, override="Y")
    global_defaults = Feature.objects.filter(app_code__isnull=True, default="Y")

    return render(
        request,
        "features/list.html",
        {
            "is_global_admin": is_global_admin,
            "app_features": app_features,
            "global_overrides": global_overrides,
            "global_defaults": global_defaults,
            "status_options": {
                "N": "Disabled",
                "Y": "Enabled",
                "L": "Limited",
            },
            "now": ConvenientDate("now"),
        },
    )


@require_authority(allowable_role_list)
def add_feature(request):
    log.trace()
    has_error = False

    # Only global admins can set global features
    is_global_admin = auth_service.has_authority(
        allowable_role_list, require_global=True
    )
    app_code = request.POST.get("app_code")
    default = override = "N"
    log.debug(f"Selected app: {app_code}")

    # Globals have null app_codes
    if is_global_admin and app_code == "global_override":
        app_code = None
        override = "Y"
    elif is_global_admin and app_code == "global_default":
        app_code = None
        default = "Y"
    # The only other option is the app_code
    else:
        app_code = utility_service.get_app_code()

    # Feature codes should be lowercase <= 30 chars
    if re.match(r"^\w{1,30}$", request.POST.get("feature_code")):
        feature_code = request.POST.get("feature_code")
    else:
        message_service.post_error("Feature codes must be 1 to 30 characters long")
        feature_code = None
        has_error = True

    # Feature titles should be <= 80 chars
    if re.match(r"^.{1,80}$", request.POST.get("feature_title")):
        feature_title = request.POST.get("feature_title")
    else:
        # Use feature code as the default
        feature_title = feature_code

    # Feature descriptions should be <= 500 chars
    if re.match(r"^.{1,80}$", request.POST.get("feature_description")):
        feature_description = request.POST.get("feature_description")[:500]
    else:
        # Use feature code as the default
        feature_description = None

    status = request.POST.get("status")
    if status is None or status not in ["Y", "N", "L"]:
        # Default status to Limited
        status = "L"

    # Enable and Disable Dates
    enable_date = disable_date = None
    enable_str = request.POST.get("enable_date")
    disable_str = request.POST.get("disable_date")
    if enable_str:
        try:
            enable_date = ConvenientDate(enable_str).datetime_instance
        except Exception as ee:
            message_service.post_error(
                f"Unable to process the given enable date: {enable_str}"
            )
    if disable_str:
        try:
            disable_date = ConvenientDate(disable_str).datetime_instance
        except Exception as ee:
            message_service.post_error(
                f"Unable to process the given disable date: {disable_str}"
            )

    if not has_error:
        log.info(f"Creating new feature: {app_code}.{feature_code}")
        new_feature = Feature(
            app_code=app_code,
            override=override,
            default=default,
            feature_code=feature_code,
            feature_title=feature_title,
            feature_description=feature_description,
            status=status,
            enable_date=enable_date,
            disable_date=disable_date,
        )
        log.info(f"Saving new feature: {new_feature}")
        new_feature.save()

    return redirect("psu:features")


@require_authority(allowable_role_list)
def modify_feature(request):
    log.trace()
    has_error = False

    # Get targeted feature
    feature_id = request.POST.get("id")
    feature_instance = get_feature(feature_id)

    prop = request.POST.get("prop")
    value = request.POST.get("value")
    log.info(f"Change {prop} to {value}")

    if prop == "title":
        value = value[:80] if value else feature_instance.feature_code
        feature_instance.feature_title = value
        feature_instance.save()
    elif prop == "description":
        value = value[:500] if value else value
        feature_instance.feature_description = value
        feature_instance.save()
    elif prop == "status":
        if value not in ["Y", "N", "L"]:
            return HttpResponseForbidden("Invalid status was given")
        else:
            feature_instance.status = value
            feature_instance.save()
    elif prop.endswith("_date"):
        value = ConvenientDate(value).datetime_instance
        setattr(feature_instance, prop, value)
        feature_instance.save()
    else:
        return HttpResponseForbidden("Invalid property was selected")

    return HttpResponse(value)


@require_authority(allowable_role_list)
def delete_feature(request):
    log.trace()

    # Get targeted feature
    feature_id = request.POST.get("id")
    feature_instance = get_feature(feature_id)
    feature_instance.delete()
    return HttpResponse("success")


def get_feature(feature_id):
    """
    Get a feature from the given ID for the purpose of editing.
    Validate appropriate permissions to edit the feature
    """
    log.trace()

    # Get targeted feature
    feature_instance = Feature.objects.get(pk=feature_id)

    if not feature_instance:
        raise Http404("Feature not found")

    # Only global admins can change global features
    if feature_instance.app_code is None:
        is_global_admin = auth_service.has_authority(
            allowable_role_list, require_global=True
        )
        if not is_global_admin:
            message_service.post_error("Only global admins may modify global features")
            raise HttpResponseNotAllowed(
                "Only global admins may modify global features"
            )

    # Otherwise, return the feature
    return feature_instance
