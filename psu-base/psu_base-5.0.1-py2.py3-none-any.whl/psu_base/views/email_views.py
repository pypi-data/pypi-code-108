# testing_views.py
#
#   These are views that are used for debugging or testing the status of an app
#

from django.shortcuts import render
from django.http import HttpResponse, Http404
from psu_base.classes.ConvenientDate import ConvenientDate
from psu_base.classes.Log import Log
from psu_base.services import (
    utility_service,
    email_service,
    message_service,
    auth_service,
)
from psu_base.decorators import require_authority
from psu_base.models.email import Email
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.db.models import Q
from datetime import timedelta
import re

log = Log()
allowable_role_list = ["~power_user"]


@require_authority(allowable_role_list)
def email_list(request):
    """
    Show emails sent from this app
    """
    # Get pagination data from session and/or params
    sortby, page, keywords = utility_service.pagination_sort_info(
        request, "date_created", "desc", filter_name="keywords"
    )

    # Emails sent from this app
    app_code = utility_service.get_app_code()
    app_emails = Email.objects.filter(app_code=app_code)

    if keywords:
        for ww in keywords.split():
            if ww and len(ww) > 2:

                # If keyword is an email address
                if "@" in ww:
                    # If type of email was specified
                    if ":" in ww:
                        pieces = ww.split(":")
                        if len(pieces[1]) <= 2:
                            continue
                        elif pieces[0].lower() == "to":
                            app_emails = app_emails.filter(to__icontains=pieces[1])
                        elif pieces[0].lower() == "cc":
                            app_emails = app_emails.filter(cc__icontains=pieces[1])
                        elif pieces[0].lower() == "bcc":
                            app_emails = app_emails.filter(bcc__icontains=pieces[1])
                        elif pieces[0].lower() in ["from", "sender"]:
                            app_emails = app_emails.filter(sender__icontains=pieces[1])
                        else:
                            app_emails = app_emails.filter(
                                Q(to__icontains=pieces[1])
                                | Q(cc__icontains=pieces[1])
                                | Q(bcc__icontains=pieces[1])
                            )
                    # Otherwise check all recipient types (not sender)
                    else:
                        app_emails = app_emails.filter(
                            Q(to__icontains=ww)
                            | Q(cc__icontains=ww)
                            | Q(bcc__icontains=ww)
                        )

                # If keyword is a path
                elif "/" in ww:
                    app_emails = app_emails.filter(url__icontains=ww)

                # Handle some specified properties
                elif ":" in ww:
                    pieces = ww.split(":")

                    # This could still be part of the subject
                    if len(pieces[1]) <= 2:
                        app_emails = app_emails.filter(subject__icontains=ww)

                    elif pieces[0].lower() in [
                        "before",
                        "after",
                        "on",
                        "since",
                        "initiator",
                        "by",
                    ]:
                        # If date is expected
                        if pieces[0].lower() in ["before", "after", "on", "since"]:
                            try:
                                cd = ConvenientDate(pieces[1])
                                log.debug(f"CD: {cd}")
                                if pieces[0].lower() == "before":
                                    app_emails = app_emails.filter(
                                        date_created__lt=cd.datetime_instance
                                    )
                                elif pieces[0].lower() in ["after", "since"]:
                                    app_emails = app_emails.filter(
                                        date_created__gte=cd.datetime_instance
                                    )
                                else:
                                    next_day = cd.datetime_instance + timedelta(days=1)
                                    app_emails = app_emails.filter(
                                        date_created__gte=cd.datetime_instance
                                    )
                                    app_emails = app_emails.filter(
                                        date_created__lt=next_day
                                    )
                            except Exception as ee:
                                message_service.post_warning(
                                    f"Could not determine date from '{pieces[1]}'"
                                )
                                log.debug(ee)

                        # If specifying the initiator
                        elif pieces[0].lower() in ["initiator", "by"]:
                            app_emails = app_emails.filter(
                                initiator__icontains=pieces[1]
                            )
                    else:
                        # Treat as part of the subject, which may have contained a ':'
                        app_emails = app_emails.filter(subject__icontains=ww)

                # For all other keywords, look at subject
                else:
                    app_emails = app_emails.filter(subject__icontains=ww)

    # Sort results
    app_emails = app_emails.order_by(*sortby)

    # Paginate the results
    paginator = Paginator(app_emails, 50)
    app_emails = paginator.get_page(page)

    return render(
        request, "email/list.html", {"app_emails": app_emails, "keywords": keywords}
    )


@require_authority(allowable_role_list)
def display_email(request):
    """Display one logged email"""
    email_id = request.GET.get("id")
    email_instance = None

    if id:
        email_instance = Email.objects.get(pk=email_id)

    if email_instance:

        # Message content can be displayed from template (html or text) or plain-text content
        message_content = None

        if email_instance.email_template:
            template = email_instance.email_template

            # User objects break the eval and must be replaced
            if email_instance.context:
                try:
                    context = re.sub(
                        r"<(\w+):[^>]+>",
                        r"auth_service.look_up_user_cache('\1')",
                        email_instance.context,
                    )
                    context = eval(context)
                except Exception as ee:
                    message_service.post_warning(
                        "Email may not display correctly. Resending it is not recommended."
                    )
                    log.warning(f"Error displaying email: {ee}")
                    context = {}
            else:
                context = {}

            # Try an HTML template
            try:
                message_content = render_to_string(f"{template}.html", context)
            except Exception as ee:
                log.debug("No html template for given email")

            # Try plain-text template
            if not message_content:
                try:
                    message_content = render_to_string(f"{template}.txt", context)
                except Exception as ee:
                    log.debug("No txt template for given email")

        # Use plain-text content
        if not message_content:
            message_content = email_instance.content

        return render(
            request,
            "email/instance.html",
            {"email_instance": email_instance, "message_content": message_content},
        )

    else:
        raise Http404("Email not found")


@require_authority(allowable_role_list)
def resend_email(request):
    """Resend one logged email"""
    email_id = request.POST.get("id")
    email_instance = None
    if id:
        email_instance = Email.objects.get(pk=email_id)

    if email_instance:
        to = email_instance.get_to_list()
        cc = email_instance.get_cc_list()
        bcc = email_instance.get_bcc_list()
        num_recipients = (
            (len(to) if to else 0) + (len(cc) if cc else 0) + (len(bcc) if bcc else 0)
        )

        # User objects break the eval and must be replaced
        if email_instance.context:
            try:
                context = re.sub(
                    r"<(\w+):[^>]+>",
                    r"auth_service.look_up_user_cache('\1')",
                    email_instance.context,
                )
                context = eval(context)
            except Exception as ee:
                message_service.post_warning(
                    "Email may not display correctly. Resending it is not recommended."
                )
                log.warning(f"Error displaying email: {ee}")
                context = {}
        else:
            context = {}

        email_service.send(
            subject=email_instance.subject,
            content=email_instance.content,
            sender=email_instance.sender,
            to=to,
            cc=cc,
            bcc=bcc,
            email_template=email_instance.email_template,
            context=context,
            test_group_codes=None,
            max_recipients=num_recipients,
        )

        return HttpResponse("Message Resent")

    else:
        raise Http404("Email not found")
