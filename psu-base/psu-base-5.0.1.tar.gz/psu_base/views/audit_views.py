# audit_views.py
#
#   These are views that are used for auditing events
#

from django.shortcuts import render
from psu_base.services import utility_service, auth_service, message_service
from psu_base.decorators import require_authority
from psu_base.models.audit import Audit
from psu_base.models.xss import Xss
from django.db.models import Q
from django.http import HttpResponseNotAllowed, Http404, HttpResponse
from psu_base.classes.Log import Log
from psu_base.classes.ConvenientDate import ConvenientDate
from psu_base.classes.User import User
from django.core.paginator import Paginator

log = Log()
allowable_role_list = ["~securityOfficer"]


@require_authority(allowable_role_list)
def audit_list(request):
    """
    List audit events
    """
    # Get a list of all audit event codes (for filtering)
    event_codes = Audit.objects.values("event_code").distinct()

    # Initialize filter variables
    ff = {
        "username": None,
        "sso": None,
        "impersonated": None,
        "proxied": None,
        "from_date": None,
        "to_date": None,
        "from_date_display": None,
        "to_date_display": None,
        "event_code": None,
        "reference": None,
        "comment": None,
    }
    user_instance = None

    # Were filters updated/submitted?
    if request.GET.get("filter_submission"):

        # Get user filters
        ff["username"] = request.GET.get("username")
        user_types = request.GET.getlist("user_type")
        if user_types:
            ff["sso"] = "S" in user_types
            ff["impersonated"] = "I" in user_types
            ff["proxied"] = "P" in user_types
        # Provide default user_type if none selected
        if ff["username"] and (not ff["impersonated"]) and (not ff["proxied"]):
            ff["sso"] = True

        # Get date filters
        ff["from_date"] = request.GET.get("from_date")
        ff["to_date"] = request.GET.get("to_date")

        # Get event filter
        ff["event_code"] = request.GET.getlist("event_code")

        # Get reference filter
        ff["reference"] = request.GET.get("reference")

        # Get comment filter
        ff["comment"] = request.GET.get("comment")

        # Save selections for future requests (pagination)
        utility_service.set_session_var("audit_filter_selections", ff)

    # Otherwise, look for saved filters
    else:
        ff = utility_service.get_session_var("audit_filter_selections", ff)

    # Look up user info
    if ff["username"]:
        user_instance = User(ff["username"])  # also accepts PSU ID or pidm

    # Get convenient date instances
    from_date_instance = ConvenientDate(ff["from_date"])
    to_date_instance = ConvenientDate(ff["to_date"])

    # Get pagination data from session and/or params
    sortby, page, ff["comment"] = utility_service.pagination_sort_info(
        request, "date_created", "desc", filter_name="comment"
    )

    # Start building the query
    audits = Audit.objects.filter(app_code=utility_service.get_app_code())
    filtered = False

    if ff["username"]:
        # Get the username. If PSU ID was given, will need to get username from user_instance
        query_user = ff["username"] if user_instance is None else user_instance.username
        if ff["sso"]:
            if filtered:
                audits = audits | Audit.objects.filter(Q(username=query_user))
            else:
                audits = Audit.objects.filter(Q(username=query_user))
                filtered = True
        if ff["impersonated"]:
            if filtered:
                audits = audits | Audit.objects.filter(
                    Q(impersonated_username=query_user)
                )
            else:
                audits = Audit.objects.filter(Q(impersonated_username=query_user))
                filtered = True
        if ff["proxied"]:
            if filtered:
                audits = audits | Audit.objects.filter(Q(proxied_username=query_user))
            else:
                audits = Audit.objects.filter(Q(proxied_username=query_user))
                filtered = True

    if ff["from_date"]:
        # Must be in proper timestamp format (with hours and minutes)
        ff["from_date"] = from_date_instance.timestamp()
        if filtered:
            audits = audits & Audit.objects.filter(Q(date_created__gte=ff["from_date"]))
        else:
            audits = Audit.objects.filter(Q(date_created__gte=ff["from_date"]))
            filtered = True

    if ff["to_date"]:
        # Must be in proper timestamp format (with hours and minutes)
        ff["to_date"] = to_date_instance.timestamp()
        if filtered:
            audits = audits & Audit.objects.filter(Q(date_created__lte=ff["to_date"]))
        else:
            audits = Audit.objects.filter(Q(date_created__lte=ff["to_date"]))
            filtered = True

    if ff["event_code"]:
        empty_list = str(ff["event_code"]) == "['']"
        if not empty_list:
            if filtered:
                audits = audits & Audit.objects.filter(
                    Q(event_code__in=ff["event_code"])
                )
            else:
                audits = Audit.objects.filter(Q(event_code__in=ff["event_code"]))
                filtered = True
        else:
            ff["event_code"] = None

    if ff["reference"]:
        for ww in ff["reference"].split():
            if ww.isnumeric():
                q = Q(reference_id=ww)
            else:
                q = Q(reference_code__icontains=ww)
            if filtered:
                audits = audits & Audit.objects.filter(q)
            else:
                audits = Audit.objects.filter(q)
                filtered = True

    if ff["comment"]:
        if filtered:
            audits = audits & Audit.objects.filter(Q(event_code__in=ff["comment"]))
        else:
            audits = Audit.objects.filter(Q(comments__icontains=ff["comment"]))
            filtered = True

    if not filtered:
        audits = audits.all()

    # Get sort, order, and page
    audits = audits.order_by(*sortby)

    paginator = Paginator(audits, 50)
    audits = paginator.get_page(page)

    return render(
        request,
        "audit/list.html",
        {
            "audits": audits,
            "ff": ff,
            "user_instance": user_instance,
            "event_codes": {
                result["event_code"]: result["event_code"] for result in event_codes
            },
            "from_date_instance": from_date_instance,
            "to_date_instance": to_date_instance,
        },
    )


@require_authority(allowable_role_list)
def audit_xss_attempts(request):
    """
    List XSS attempts
    """

    auth = auth_service.get_auth_object()
    username_sso = username = auth.get_user().username
    if auth.is_impersonating():
        username_sso = auth.sso_user.username

    # Get a list of all XSS attempts
    xss = Xss.objects.filter(review_username__isnull=True).order_by("-date_created")
    paginator = Paginator(xss, 50)
    page = request.GET.get("page", 1)
    xss = paginator.get_page(page)

    return render(
        request,
        "audit/xss.html",
        {"xss": xss, "username": username, "username_sso": username_sso},
    )


@require_authority(allowable_role_list)
def audit_xss_review_attempt(request):
    """
    Review an XSS attempt
    """
    xss_id = request.POST.get("id", 0)
    xss_instance = get_xss(xss_id)
    xss_instance.review_username = auth_service.get_user().username
    xss_instance.save()

    # Also log it in the audit table.
    auth_service.audit_event(
        "xss_review", comments=f"Reviewed attempt #{xss_id} by {xss_instance.username}"
    )

    return HttpResponse("success")


def get_xss(xss_id):
    """
    Get xss from the given ID for the purpose of editing.
    Validate appropriate permissions to edit the xss
    """
    log.trace()

    auth = auth_service.get_auth_object()
    username_sso = username = auth.get_user().username
    if auth.is_impersonating():
        username_sso = auth.sso_user.username

    # Get targeted xss
    xss_instance = Xss.objects.get(pk=xss_id)

    if not xss_instance:
        raise Http404("XSS not found")

    # Cannot review your own XSS
    if xss_instance.username in [username, username_sso]:
        message_service.post_error("You cannot review your own XSS attempts")
        raise HttpResponseNotAllowed("You cannot review your own XSS attempts")

    # Otherwise, return the xss
    return xss_instance
