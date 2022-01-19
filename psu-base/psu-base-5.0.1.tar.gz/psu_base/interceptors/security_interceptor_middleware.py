from django.shortcuts import redirect
from psu_base.services import utility_service, auth_service, message_service
from psu_base.classes.Log import Log
from psu_base.models.xss import Xss
from django.urls import reverse
from django.http import HttpResponseForbidden, HttpResponse

log = Log()


def xss_prevention(get_response):
    def script_response(param, value, is_ajax, path):

        # Log the suspicious parameter
        log.error(f"Potential XSS attempt in '{param}' parameter")
        log.info(f"\n{value}\n")

        # In prod, store the attempt as being from the CAS user
        # In non-prod, use the impersonated user for testing
        auth_object = auth_service.get_auth_object()
        if utility_service.is_production():
            xss_username = auth_object.sso_user.username
        else:
            xss_username = auth_object.get_user().username

        # Store attempt in database.
        xss_instance = Xss(
            app_code=utility_service.get_app_code(),
            path=path,
            username=xss_username,
            parameter_name=param,
            parameter_value=value,
        )
        xss_instance.save()

        # Also log it in the audit table.
        auth_service.audit_event(
            "xss_attempt", comments=f"Created XSS attempt record #{xss_instance.id}"
        )

        if is_ajax:
            # Generate a "flash message" to display on the view
            message_service.post_error(
                "Suspicious input detected. Unable to process request."
            )

            # Return as failure for AJAX calls
            return HttpResponseForbidden()
        else:
            # Redirect to "suspicious input" page for non-AJAX requests
            return redirect("psu:xss")

    def xss_middleware(request):

        # Gather conditions and values used later
        is_health_check = utility_service.is_health_check()
        is_flash_messages = request.path == reverse("psu:messages")
        is_xss_lock = request.path == reverse("psu:xss_lock")
        is_terminating_impersonation = request.path == reverse("psu:stop_impersonating")
        is_logging_out = request.path == reverse("psu:logout")
        username = auth_service.get_user().username
        is_ajax = utility_service.is_ajax()

        # Script_response will return a redirect.  If there are multiple XSS attempts, all attempts
        # should be logged, but only one return is needed. Store it in a variable while iterating.
        script_response_value = None

        # Iterate through GET parameters
        for param, value in request.GET.items():
            if utility_service.contains_script(value):
                # If XSS attempt found, log it and get a Redirect
                script_response_value = script_response(
                    param, value, is_ajax, request.path
                )

        # Iterate through POST parameters
        for param, value in request.POST.items():
            if utility_service.contains_script(value):
                # If XSS attempt found, log it and get a Redirect
                script_response_value = script_response(
                    param, value, is_ajax, request.path
                )

        # If xss was found, return the Redirect to the blocking page
        if script_response_value is not None:
            return script_response_value

        # If not already loading the lock page (and not an AWS health check)
        if username is not None and not (
            is_xss_lock or is_health_check or is_flash_messages
        ):
            # Locked out users may logout or stop impersonating
            if not (is_terminating_impersonation or is_logging_out):
                # Count the number of un-reviewed XSS attempts for this user
                attempts = len(
                    Xss.objects.filter(username=username, review_username__isnull=True)
                )
                # After 3 attempts, user is locked out of site
                if attempts >= 3:
                    return redirect("psu:xss_lock")

        # Otherwise, continue normally (and add XSS-Protection header)
        response = get_response(request)
        if type(response) is HttpResponse:
            response["X-XSS-Protection"] = "1"

            # Also add Cache-control: no-store and Pragma: no-cache headers (recommended by security team)
            response["Cache-Control"] = "no-store"
            response["Pragma"] = "no-cache"
        # else:
        #     log.info(f"Security headers not added to {type(response)}")

        return response

    return xss_middleware
