import re
from pathlib import Path

try:
    from extools.view import exview
    from extools.view.errors import (
            ExViewInterpolationError, ExViewRecordDoesNotExist)
    from extools.message import logger_for_module
    from accpac import Email
except ImportError as e:
    # This happens when the tools are imported outside of the Extender env.
    # We can pass to let the tool do its work (likely sphinx making docs).
    pass

FIELD_REGEX = re.compile(r'{\s*[A-Z]{2}\d{4}\.[A-Z]+\s*}')

def get_email_template(message_id, tmpl_view="VI0008"):
    """Get a message template from the database.

    Retrieves a message from the database and returns the subject and
    body::

        subj, body= get_email_template("MODULE.ORDERCONFIRM")

    :param message_id: Extender Message ID to open.
    :type message_id: str
    :returns: (subject, body)
    :rtype: (str, str)
    """
    subj = ""
    body = ""

    try:
        with exview(tmpl_view, seek_to={'MSGID': message_id}) as vVIMSG:
            subj = vVIMSG.get("SUBJECT").strip()
            body = vVIMSG.get("BODY")
            for i in range(2,10):
                body += vVIMSG.get("BODY"+str(i))
    except ExViewRecordDoesNotExist:
        return ("", "")

    return subj, body

def get_and_render_email_template(
        message_id, root_view, seek_to, format_vars={}, tmpl_view="VI0008"):
    """Get a message template from the database and render using the root view.

    Retrieves a message from the database and interpolates values from the root
    view or any view with which it composes.

    Arbitrary format strings can also be provided.

    Example template for an O/E Order::

        Hello {OE0520.CUSTOMER},

        Thank you for your order! Your order number is {OE0520.ORDNUMBER}.

        The order is shipping to:
            {OE0520.SHPADDR1}
            {OE0520.SHPADDR2}
            {OE0520.SHPADDR3}
            {OE0520.SHPCITY} {OE0520.SHPZIP} {OE0520.SHPSTATE}

        Best,

        {user}

    This message (assume id "MODULE.ORDERCONFIRM") can be rendered for
    for ORD00001::

        subj, body= get_and_render_email_template(
                        "MODULE.ORDERCONFIRM", "OE0520",
                        seek_to={'ORDNUMBER': "ORD00001"},
                        format_vars={'user': user})

    :param message_id: Extender Message ID to open.
    :type message_id: str
    :param root_view: Roto ID of the root view to user when rendering.
    :type root_view: str
    :param seek_to: key value pairs for a valid unique index.
    :type: dict
    :params format_vars: additional format variables specific to the user case.
    :type: dict
    :params tmpl_view: view to extract the template from (i.e. VI or EFT template).
    :type tmpl_view: str (VI0008 or EL0007)
    """
    subj, body = get_email_template(message_id, tmpl_view)
    subj = interpolate(subj, root_view, seek_to)
    body = interpolate(body, root_view, seek_to)

    if format_vars:
        subj = subj.format(**format_vars)
        body = body.format(**format_vars)

    return subj, body

def send_email(subj, body, to, cc="", bcc="", reply_to="",
               attach="", attach_mimetype='application/pdf'):
    """Send an email with optional attachments.

    Wrapper for email sending that supports multiple argument formats
    and tries to do the right thing.

    :param subj: Email subject.
    :type subj: str
    :param body: Email body.
    :type body: str
    :param to: One or many addresses. Semi-colon (;) separated also supported.
    :type to: str or [str, ]
    :param cc: One or many addresses. Semi-colon (;) separated also supported.
    :type cc: str or [str, ]
    :param bcc: One or many addresses. Semi-colon (;) separated also supported.
    :type bcc: str or [str, ]
    :param reply_to: An email address to set in the Reply-To field.
    :type reply_to: str
    :param attach: Files to attach to the email. Either a filename or a tuple
                   (file path, mimetype).
    :type attach: [str, ] or [(str, str), ]
    :param attach_mimetype: Mimetype to use for attachments if not
                            specified in tuple. Defaults to ``application/pdf``
    :returns: True if no error, else False
    :rtype: bool
    """

    log = logger_for_module('extools')
    log.info("send_email({}, {}, {}, {}, {}, {}, {}, {})".format(
            subj, body, to, cc, bcc, reply_to, attach, attach_mimetype))

    if isinstance(to, list):
        to = ';'.join(to)
    if isinstance(cc, list):
        cc = ';'.join(cc)
    if isinstance(bcc, list):
        bcc = ';'.join(bcc)

    m = Email()
    m.setTo(to)
    m.setCC(cc)
    m.setBCC(bcc)
    m.setSubject(subj)
    if body.startswith("<"):
        m.setHtml(body)
    else:
        m.setText(body)

    if reply_to:
        m.setReplyTo(reply_to)

    if attach:
        log.debug("attachments provided: {}".format(attach))
        if isinstance(attach, str):
            m.attach(attach, attach_mimetype)
        elif isinstance(attach, Path):
            m.attach(str(attach), attach_mimetype)
        elif isinstance(attach, tuple):
            if len(attach) == 2:
                m.attach(str(attach[0]), str(attach[1]))
        elif isinstance(attach, list):
            log.debug("attaching from list.")
            for attachment in attach:
                if isinstance(attachment, tuple) and len(attachment) == 2:
                    r = m.attach(str(attachment[0]), str(attachment[1]))
                else:
                    r = m.attach(str(attachment), attach_mimetype)
                log.debug("attach {}: {}".format(attach, r))

    r = m.send()
    if r != 0:
        return False

    return True

def interpolate(format_string, root_view, seek_to=""):

    fields = [f.strip("{} \t") for f in FIELD_REGEX.findall(format_string)]
    view_ids = { a.split('.')[0] for a in fields }
    result_string = format_string

    with exview(root_view, seek_to=seek_to, index=90) as exv:
        exv.compose()

        for view_id in view_ids:
            if not (view_id == root_view or hasattr(exv, view_id.lower())):
                raise ExViewInterpolationError(
                        view_id, format_string, None, root_view, seek_to)
        for field in fields:
            view_id, field_name = field.split(".")
            try:
                if root_view == view_id:
                    value = exv.get(field_name)
                else:
                    value = getattr(exv, view_id.lower()).get(field_name)
            except:
                raise ExViewInterpolationError(
                        view_id, format_string, field, root_view, seek_to)
            result_string = re.sub("{{{}}}".format(field), value, result_string)

    return result_string
