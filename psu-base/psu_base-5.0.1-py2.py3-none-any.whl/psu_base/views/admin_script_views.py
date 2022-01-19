# testing_views.py
#
#   These are views that are used for debugging or testing the status of an app
#

from django.shortcuts import render
from django.shortcuts import redirect
from psu_base.services import utility_service, auth_service, message_service
from psu_base.decorators import require_authority
from psu_base.models.admin_script import AdminScript
from django.http import (
    HttpResponseNotAllowed,
    Http404,
    HttpResponseForbidden,
    HttpResponse,
)
from psu_base.classes.Log import Log

log = Log()
allowable_role_list = ["~super_user", "scriptor"]


@require_authority(allowable_role_list)
def script_list(request):
    """
    List all scripts for this application
    """
    # Can the user manage scripts for ALL apps?
    is_global_admin = auth_service.has_authority(
        allowable_role_list, require_global=True
    )

    # Get all scripts (app and globals)
    app_scripts = AdminScript.objects.filter(app_code=utility_service.get_app_code())
    global_scripts = AdminScript.objects.filter(app_code__isnull=True)

    return render(
        request,
        "scripts/list.html",
        {
            "is_global_admin": is_global_admin,
            "app_scripts": app_scripts,
            "global_scripts": global_scripts,
            "enabled_options": {"N": "Disabled", "Y": "Enabled"},
        },
    )


@require_authority(allowable_role_list)
def add_script(request):
    log.trace()

    # Only global admins can set global scripts
    is_global_admin = auth_service.has_authority(
        allowable_role_list, require_global=True
    )
    app_code = request.POST.get("app_code")
    log.debug(f"Selected app: {app_code}")

    # Globals have null app_codes
    if is_global_admin and not app_code:
        app_code = None
    # The only other option is the app_code
    else:
        app_code = utility_service.get_app_code()

    # Get all other parameters
    target_username = request.POST.get("target_username")
    target_url = request.POST.get("target_url")
    enabled = request.POST.get("enabled", "N")
    eff_date = request.POST.get("eff_date")
    end_date = request.POST.get("end_date")
    javascript = request.POST.get("javascript")
    description = request.POST.get("description")

    # Check for issues in parameters
    has_error = False
    if target_username and len(target_username) > 30:
        has_error = True
        log.error("Target username is too long")
    if target_url and len(target_url) > 80:
        has_error = True
        log.error("Target URL is too long")
    if (not javascript) or len(javascript) > 4000:
        has_error = True
        log.error("Script is required and must be no more than 4k characters")
    if (not description) or len(description) > 100:
        has_error = True
        log.error("Description is required and must be no more than 100 characters")

    if enabled is None or enabled not in ["Y", "N"]:
        status = "N"  # Default enabled to N

    if not has_error:
        log.info(f"Creating new script: {app_code if app_code else 'Global'}")
        new_script = AdminScript(
            app_code=app_code,
            developer=auth_service.get_user().username,
            target_username=target_username,
            target_url=target_url,
            enabled=enabled,
            eff_date=eff_date if eff_date else None,
            end_date=end_date if end_date else None,
            description=description,
            javascript=javascript,
        )
        log.info(f"Saving new script: {new_script}")
        new_script.save()

        # Audit this event, which should be a relatively rare occurrence
        auth_service.audit_event(
            "admin_script",
            new_value=javascript[:500],
            comments=f"Created a new {app_code if app_code else 'GLOBAL'} script",
        )

    return redirect("psu:scripts")


@require_authority(allowable_role_list)
def modify_script(request):
    log.trace()
    has_error = False

    # Get targeted script
    script_id = request.POST.get("id")
    script_instance = get_script(script_id)

    prop = request.POST.get("prop")
    value = request.POST.get("value")
    previous_value = None

    log.info(f"Change {prop} to {value}")

    if prop == "target_url":
        previous_value = script_instance.target_url
        script_instance.target_url = value
    elif prop == "target_username":
        previous_value = script_instance.target_username
        script_instance.target_username = value
    elif prop == "eff_date":
        previous_value = script_instance.eff_date
        script_instance.eff_date = value
    elif prop == "end_date":
        previous_value = script_instance.end_date
        script_instance.end_date = value
    elif prop == "description":
        if not value:
            return HttpResponseForbidden("Description is required")
        previous_value = script_instance.description
        script_instance.description = value
    elif prop == "enabled":
        previous_value = script_instance.enabled
        if value not in ["Y", "N"]:
            return HttpResponseForbidden("Invalid value was given for enabled")
        else:
            script_instance.enabled = value
    elif prop == "javascript":
        previous_value = script_instance.javascript
        script_instance.javascript = value
    else:
        return HttpResponseForbidden("Invalid property was selected")

    log.info(f"Changing {prop} to {value}")

    script_instance.developer = auth_service.get_user().username
    script_instance.save()

    # Audit this event, which should be a relatively rare occurrence
    auth_service.audit_event(
        "admin_script",
        previous_value=previous_value[:500] if previous_value else previous_value,
        new_value=value,
        comments="Modified existing script",
    )

    return HttpResponse(value)


@require_authority(allowable_role_list)
def delete_script(request):
    log.trace()

    # Get targeted script
    script_id = request.POST.get("id")
    script_instance = get_script(script_id)
    script_instance.delete()
    return HttpResponse("success")


def get_script(script_id):
    """
    Get a script from the given ID for the purpose of editing.
    Validate appropriate permissions to edit the script
    """
    log.trace()

    # Get targeted script
    script_instance = AdminScript.objects.get(pk=script_id)

    if not script_instance:
        raise Http404("Script not found")

    # Only global admins can change global scripts
    if script_instance.app_code is None:
        is_global_admin = auth_service.has_authority(
            allowable_role_list, require_global=True
        )
        if not is_global_admin:
            message_service.post_error("Only global admins may modify global scripts")
            raise HttpResponseNotAllowed("Only global admins may modify global scripts")

    # Otherwise, return the script
    return script_instance
