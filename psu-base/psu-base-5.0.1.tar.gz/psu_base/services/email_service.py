from psu_base.services import auth_service
from psu_base.services import utility_service
from psu_base.services import message_service, error_service
from psu_base.classes.Finti import Finti
from psu_base.classes.Log import Log
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from psu_base.models.email import Email
from psu_base.context_processors import util as util_context, auth as auth_context
from django.urls import reverse

log = Log()


def get_authorized_emails(authority_code):
    """Get emails of users with specified authority (or authorities)"""
    auth_users = auth_service.get_authorized_users(authority_code)
    return [uu.email_address for uu in auth_users] if auth_users else []


def get_psu_context(util=True, auth=True):
    """Get psu_base context to include in all email context"""
    psu = {}
    request = utility_service.get_request()
    if auth:
        psu.update(auth_context(request))
    if util:
        psu.update(util_context(request))
    return psu


def get_absolute_url(*args):
    context = get_psu_context(util=True, auth=False)
    if args:
        return f"{context['absolute_root_url']}{reverse(args[0], args=args[1:])}"
    else:
        return context["absolute_root_url"]


def get_default_recipient():
    # When authenticated, default to CAS-authenticated user
    if auth_service.is_logged_in():
        sso_email = auth_service.get_auth_object().sso_user.email_address
        return (
            sso_email.lower().replace("gtest.", "").replace("gdev.", "")
            if sso_email
            else None
        )

    # When non-authenticated in non-production, allow a default address to be specified and stored in the session
    elif utility_service.is_non_production():
        return utility_service.get_session_var("psu_base_default_recipient")

    # Otherwise, there is no default recipient
    return None


def set_default_email(default_recipient):
    """
    When non-authenticated in non-production, a default recipient can be specified and stored in the session
    (this helps test emails for non-authenticated situations, like Dual Credit Applications)
    """
    utility_service.set_session_var("psu_base_default_recipient", default_recipient)


def get_testing_emails(group_codes=None):
    """
    Get email addresses that are allowed to receive non-production emails.
    If no group code is specified, all allowed emails will be returned.
    Group codes may be a list, or a single group code.
    If OIT is not in your list, it will be added automatically (because OIT always gets emails!)
    """
    log.trace()

    # If a single group code was given, make it a list
    if group_codes and type(group_codes) is not list:
        group_codes = [group_codes]

    # If OIT was not specified, add it automatically
    if type(group_codes) is list and "OIT" not in group_codes:
        group_codes.append("OIT")

    final_list = []
    try:
        # Get all defined groups
        all_groups = Finti(reduce_logging=True).get("wdt/v1/sso_proxy/test_groups")

        # Get the addresses associated with the specified groups
        for group_dict in all_groups:
            if group_codes is None or group_dict["group_code"] in group_codes:
                final_list.extend(group_dict["email_addresses"])

        # Make the list unique
        final_list = list(set(final_list))

    except Exception as ee:
        log.error(f"Error getting non-prod testing emails: {str(ee)}")

    return final_list


def send(
    subject=None,
    content=None,
    sender=None,
    to=None,
    cc=None,
    bcc=None,
    email_template=None,
    context=None,
    test_group_codes=None,
    max_recipients=10,  # We rarely send an email to more than 10 people. Exceptions should have to specify how many
    suppress_success_message=False,  # Do not notify user on successful send (but notify if send failed)
    suppress_status_messages=False,  # Do not notify user upon successful or failed send
    include_psu_context=True,  # Include context included on all pages (current user, environment, etc)
):
    log.trace([subject])
    invalid = False
    error_message = None

    # If sender not specified, use the default sender address
    if not sender:
        sender = utility_service.get_setting("EMAIL_SENDER")

    # Subject should never be empty.  If it is, log an error and make something up.
    if not subject:
        log.error("Email subject is empty!")
        subject = f"Message from {utility_service.get_app_name()}"

    # Non-prod emails should always point out that they're from non-prod
    if utility_service.is_non_production():
        env = utility_service.get_environment()
        prepend = f"[{env}] "
        if not (subject.startswith(env) or subject.startswith(prepend)):
            subject = f"{prepend}{subject}"

    to, cc, bcc, num_recipients = _prepare_recipients(to, cc, bcc, test_group_codes)

    # Enforce max (and min) recipients
    if num_recipients == 0:
        error_message = f"Email failed validation: No Recipients"
        log.error(error_message)
        invalid = True
    elif num_recipients > max_recipients:
        error_message = f"Email failed validation: Too Many ({num_recipients} of {max_recipients}) Recipients"
        log.error(error_message)
        invalid = True

    # If a template has not been specified, use the base template
    # (Use template=False to not use a template)
    if email_template is None:
        email_template = "email/base_template"
    # Will look for html and txt versions of the template
    template_no_ext = email_template.replace(".html", "").replace(".txt", "")
    template_html = f"{template_no_ext}.html"
    template_txt = f"{template_no_ext}.txt"

    # Standard template uses subject as page title (may not even matter?)
    if not context:
        context = {"subject": subject}
    elif "subject" not in context:
        context["subject"] = subject

    # Standard template will print plain content inside the HTML template
    if content and "content" not in context:
        context["content"] = content

    # Include standard context that psu_base injects into all pages
    if include_psu_context:
        context.update(get_psu_context())

    # Render the template to a string (HTML and plain text)
    html = plain = None
    try:
        if template_html:
            html = render_to_string(template_html, context)
    except Exception as ee:
        log.error(f"Unable to render template: {template_html}")
        log.debug(str(ee))
    try:
        if template_txt:
            plain = render_to_string(template_txt, context)
    except Exception as ee:
        if content:
            # Render the content as plain text
            plain = content
        else:
            log.warning(f"Unable to render plain-text template: {template_txt}")
            log.debug(str(ee))

    if invalid:
        log.warning(f"Email was not sent: {subject}")

    else:
        try:
            # Build the email
            email = EmailMultiAlternatives(
                subject=subject, body=plain, from_email=sender, to=to, cc=cc, bcc=bcc
            )

            # If there is an html version, attach it
            if html:
                email.attach_alternative(html, "text/html")

            # Send the email
            email.send()

        except Exception as ee:
            invalid = True
            log.error(ee)
            log.warning(f"Error sending email: {subject}")

    # Log the email
    status = "F" if invalid else "S"
    _record(
        subject=subject,
        content=content,
        sender=sender,
        to=to,
        cc=cc,
        bcc=bcc,
        email_template=email_template,
        context=context,
        max_recipients=max_recipients,
        status=status,
        error_message=error_message,
    )

    # Generate a message, either for posting or logging
    if status == "S":
        msg = ["<b>Email Sent</b><br />"]
    else:
        msg = ["<b>Unable to Send Email</b><br />"]

    msg.append('<div style="padding-left: 20px;">')

    # Include the subject
    msg.append('<span class="fa fa-envelope-o" aria-hidden="true"></span>&nbsp;')
    msg.append(f"{subject}<br />")

    # And the recipients (if not too many). Do not display Bcc
    def list_to_str(ll):
        if len(ll) > 3:
            return "(multiple recipients)"
        else:
            return str(ll).replace("'", "").replace("[", "").replace("]", "").strip()

    #
    if to:
        msg.append(f"To: {list_to_str(to)}<br />")
    if cc:
        msg.append(f"Cc: {list_to_str(cc)}<br />")

    msg.append("</div>")

    # Combine to one string
    status_message = "".join(msg)

    if not suppress_status_messages:
        # If success, and not suppressing success messages
        if status == "S" and not suppress_success_message:
            message_service.post_success(status_message)
        elif status != "S":
            message_service.post_warning(status_message)

    else:
        if status == "S":
            log.info(status_message, strip_html=True)
        else:
            log.warning(status_message, strip_html=True)

    return status == "S"


def _prepare_recipients(to, cc, bcc, test_group_codes):
    """
    Used by send() to prepare the recipients in a unit-testable way
    """
    # Recipients should be in list format
    if type(to) is not list:
        to = [to]
    if type(cc) is not list:
        cc = [cc]
    if type(bcc) is not list:
        bcc = [bcc]

    def clean(address):
        return (
            address.lower().replace("gtest.", "").replace("gdev.", "").replace(" ", "+")
        )

    # Recipient lists should be unique. To assist with this, make all emails lowercase
    to = list(set([clean(address) for address in to if address]))
    cc = list(
        set([clean(address) for address in cc if address and clean(address) not in to])
    )
    bcc = list(
        set(
            [
                clean(aa)
                for aa in bcc
                if aa and clean(aa) not in to and clean(aa) not in cc
            ]
        )
    )

    # Get the total number of recipients
    num_recipients = len(to) if to else 0
    num_recipients += len(cc) if cc else 0
    num_recipients += len(bcc) if bcc else 0

    # If this is non-production, remove any non-allowed addresses
    if utility_service.is_non_production() and num_recipients > 0:

        # In DEV, never send to anyone other than the default recipient
        if utility_service.is_development():
            testing_emails = []
        # In STAGE, use gtvsdax-defined testers from Finti
        else:
            testing_emails = get_testing_emails(test_group_codes)

        default_recipient = get_default_recipient()
        allowed_to = [
            aa for aa in to if aa in testing_emails or aa == default_recipient
        ]
        allowed_cc = [
            aa for aa in cc if aa in testing_emails or aa == default_recipient
        ]
        allowed_bcc = [
            aa for aa in bcc if aa in testing_emails or aa == default_recipient
        ]

        # Get the total number of allowed recipients
        num_allowed_recipients = len(allowed_to) if allowed_to else 0
        num_allowed_recipients += len(allowed_cc) if allowed_cc else 0
        num_allowed_recipients += len(allowed_bcc) if allowed_bcc else 0

        if num_allowed_recipients < num_recipients:
            not_allowed = {
                "to": [aa for aa in to if aa not in allowed_to],
                "cc": [aa for aa in cc if aa not in allowed_cc],
                "bcc": [aa for aa in bcc if aa not in allowed_bcc],
            }
            log.info(
                f"The following recipients were removed from the recipient list:\n{not_allowed}"
            )

        if num_allowed_recipients == 0 and default_recipient:
            message_service.post_info(
                f"No allowed non-prod recipients. Redirecting to {default_recipient}."
            )
            allowed_to = [default_recipient]
            num_allowed_recipients = 1

        return allowed_to, allowed_cc, allowed_bcc, num_allowed_recipients

    else:
        return to, cc, bcc, num_recipients


def _record(
    subject,
    content,
    sender,
    to,
    cc,
    bcc,
    email_template,
    context,
    max_recipients,
    status=None,
    error_message=None,
):
    """
    Used by send() to record emails with enough data to be able to re-send them later if needed
    """
    log.trace()

    email_instance = Email(
        app_code=utility_service.get_app_code(),
        url=utility_service.get_request().path,
        initiator=auth_service.get_auth_object().sso_user.username
        if auth_service.is_logged_in()
        else None,
        status=status,
        error_message=error_message[:128] if error_message else error_message,
        subject=subject[:128] if subject else subject,
        content=content[:4000] if content else content,
        sender=sender[:128] if sender else sender,
        to=str(to)[:4000] if to else None,
        cc=str(cc)[:4000] if cc else None,
        bcc=str(bcc)[:4000] if bcc else None,
        email_template=email_template[:128] if email_template else email_template,
        context=str(context)[:4000] if context else None,
        max_recipients=max_recipients,
    )
    email_instance.save()
