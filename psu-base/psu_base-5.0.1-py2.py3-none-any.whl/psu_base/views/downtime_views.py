# downtime_views.py
#
#   Views for setting scheduled downtimes/maintenance windows
#

from django.shortcuts import render
from django.shortcuts import redirect
from psu_base.services import utility_service, auth_service, message_service
from psu_base.decorators import require_authority
from psu_base.models.downtime import Downtime
from django.http import (
    HttpResponseNotAllowed,
    Http404,
    HttpResponseForbidden,
    HttpResponse,
)
import re
from psu_base.classes.Log import Log
from psu_base.classes.ConvenientDate import ConvenientDate
from datetime import datetime, timedelta

log = Log()
allowable_role_list = ["developer"]


@require_authority(allowable_role_list)
def downtime_list(request):
    """
    List all downtimes
    """
    downtimes = Downtime.objects.all()
    active_downtime = False
    for dt in downtimes:
        if dt.is_active():
            active_downtime = True

    return render(
        request,
        "downtimes/list.html",
        {
            "downtimes": downtimes,
            "active_downtime": active_downtime,
        },
    )


@require_authority(allowable_role_list)
def downtime_add(request):
    """
    Add a downtime
    """
    now = datetime.now()
    from_date = until_date = None

    # Get (and validate) from date
    from_date_str = request.POST.get("from_date")
    if from_date_str and from_date_str.lower() == "now":
        from_date = now
    elif from_date_str:
        from_cd = ConvenientDate(from_date_str)
        if from_cd and from_cd.datetime_instance:
            from_date = from_cd.datetime_instance

    if not from_date:
        message_service.post_error("A valid from date is required")
        return redirect("psu:downtimes")

    # If start date has passed, update to now for more accurate downtime date stamp
    if from_date < now:
        from_date = now

    # If end date was given, it must be valid
    until_date_str = request.POST.get("until_date")
    if until_date_str:
        # Can be a number of minutes
        if until_date_str.isnumeric():
            until_date = now + +timedelta(minutes=int(until_date_str))
        else:
            until_cd = ConvenientDate(until_date_str)
            if until_cd and until_cd.datetime_instance:
                until_date = until_cd.datetime_instance
        if not until_date:
            message_service.post_error("An invalid end date was given")
            return redirect("psu:downtimes")

    # Reason is optional
    reason = request.POST.get("reason")
    if not reason:
        reason = "Scheduled maintenance"

    dt = Downtime()
    dt.from_date = from_date
    dt.until_date = until_date
    dt.reason = reason
    dt.save()

    return redirect("psu:downtimes")


@require_authority(allowable_role_list)
def downtime_delete(request, downtime_id):
    """
    Delete a downtime
    """
    now = datetime.now()
    dt = Downtime.get(downtime_id)
    if dt:
        # Cannot delete a downtime that has been active
        if not dt.can_delete():
            message_service.post_error("Active downtimes cannot be deleted")
            return redirect("psu:downtimes")

        dt.delete()
    return redirect("psu:downtimes")


@require_authority(allowable_role_list)
def downtime_end(request, downtime_id):
    """
    End a downtime
    """
    now = datetime.now()
    dt = Downtime.get(downtime_id)
    if dt:
        if not dt.can_end():
            message_service.post_error("Only active downtimes can be ended")
            return redirect("psu:downtimes")

        dt.until_date = now
        dt.save()

    return redirect("psu:downtimes")
