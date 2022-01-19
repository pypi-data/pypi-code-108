# testing_views.py
#
#   These are views that are used for debugging or testing the status of an app
#

from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseForbidden
from psu_base.classes.Log import Log
from psu_base.classes.ConvenientDate import ConvenientDate
from psu_base.services import utility_service, message_service, auth_service
from psu_base.decorators import require_authority, trace
from psu_base.models.error import Error
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.db.models import Q
from datetime import timedelta

log = Log()
allowable_role_list = ["~super_user"]


@require_authority(allowable_role_list)
def error_list(request):
    """
    Show errors encountered in this app
    """
    # Errors from this app
    app_code = utility_service.get_app_code()

    sort, page, error_filter = utility_service.pagination_sort_info(
        request, "date_created", "desc", "error_filter"
    )

    if not error_filter:
        app_errors = (
            Error.objects.filter(app_code=app_code)
            .exclude(status="R")
            .exclude(status="I")
        )
    else:
        app_errors = Error.objects.filter(app_code=app_code)

        for ww in error_filter.split():
            if ww and len(ww) > 2:

                # If keyword is a path
                if "/" in ww:
                    app_errors = app_errors.filter(path__icontains=ww)

                # Handle some specified properties
                elif ":" in ww:
                    pieces = ww.split(":")

                    # This could still be part of an error message
                    if len(pieces[1]) <= 2:
                        app_errors = app_errors.filter(
                            Q(error_friendly__icontains=ww)
                            | Q(error_system__icontains=ww)
                        )

                    # If date is expected
                    elif pieces[0].lower() in ["before", "after", "on", "since"]:
                        try:
                            cd = ConvenientDate(pieces[1])
                            if pieces[0].lower() == "before":
                                app_errors = app_errors.filter(
                                    date_created__lt=cd.datetime_instance
                                )
                            elif pieces[0].lower() in ["after", "since"]:
                                app_errors = app_errors.filter(
                                    date_created__gte=cd.datetime_instance
                                )
                            else:
                                next_day = cd.datetime_instance + timedelta(days=1)
                                app_errors = app_errors.filter(
                                    date_created__gte=cd.datetime_instance
                                )
                                app_errors = app_errors.filter(
                                    date_created__lt=next_day
                                )
                        except Exception as ee:
                            message_service.post_warning(
                                f"Could not determine date from '{pieces[1]}'"
                            )
                            log.debug(ee)
                    # If user is expected
                    elif pieces[0].lower() in [
                        "user",
                        "username",
                        "pidm",
                        "psu_id",
                        "psu-id",
                    ]:
                        user = auth_service.look_up_user_cache(pieces[1])
                        if user:
                            u = user.username
                            app_errors = app_errors.filter(
                                Q(sso_user=u)
                                | Q(impersonated_user=u)
                                | Q(proxied_user=u)
                            )
                        else:
                            message_service.post_warning(f"{pieces[0]} not found")
                    else:
                        # Treat as part of the error, which may have contained a ':'
                        app_errors = app_errors.filter(
                            Q(error_friendly__icontains=ww)
                            | Q(error_system__icontains=ww)
                        )

                elif ww.isnumeric():
                    user = auth_service.look_up_user_cache(ww)
                    if user:
                        un = user.username
                        app_errors = app_errors.filter(
                            Q(sso_user=un)
                            | Q(impersonated_user=un)
                            | Q(proxied_user=un)
                        )
                    else:
                        app_errors = app_errors.filter(
                            Q(error_friendly__icontains=ww)
                            | Q(error_system__icontains=ww)
                        )

                # For all other keywords, look at error messages and sso-usernames
                else:
                    app_errors = app_errors.filter(
                        Q(error_friendly__icontains=ww)
                        | Q(error_system__icontains=ww)
                        | Q(sso_user=ww)
                    )

    # Sort results
    app_errors = app_errors.order_by(*sort)

    # Paginate the results
    paginator = Paginator(app_errors, 50)
    app_errors = paginator.get_page(page)

    status_options = {"N": "New", "I": "Ignored", "R": "Resolved", "W": "Watch"}

    return render(
        request,
        "error/list.html",
        {
            "app_errors": app_errors,
            "status_options": status_options,
            "error_filter": error_filter,
        },
    )


@require_authority(allowable_role_list)
def error_status(request):
    """
    Set error status
    """
    if request.method == "POST":
        error_id = request.POST.get("error_id")
        new_status = request.POST.get("new_status")
        if error_id and new_status:
            ee = Error.objects.get(pk=int(error_id))
            ee.status = new_status
            ee.save()
            return HttpResponse(new_status)
    return HttpResponseForbidden()


@trace()
def authentication_error(request):
    return render(request, "error/authentication_error.html", {})
