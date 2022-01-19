from psu_base.classes.Log import Log
from psu_base.services import utility_service
from django.contrib import messages

log = Log()


def post_info(msg):
    return post_message(msg, "info")


def post_success(msg):
    return post_message(msg, "success")


def post_warning(msg):
    return post_message(msg, "warning")


def post_error(msg):
    return post_message(msg, "error")


def post_delayed_message(msg, level):
    """
    Post a message the next time a page is loaded (after the current page)
    Use case: An AJAX request encounters an error that will require a full page reload.  In this case,
    the flash messages would post, then a Javascript refresh would immediately clear the message from the screen.
    This function holds the message in the flash scope and posts it after the JS-initiated refresh.
    LIMIT 1 MESSAGE PER TYPE (info, warning, etc)
    """
    log.trace([msg, level])
    utility_service.set_flash_variable(f"delayed_message:{level.lower()}", msg)


def post_message(msg, msg_type):
    request = utility_service.get_request()
    message = str(msg)
    msg_level = getattr(messages, msg_type.upper())

    if request is None:
        log.error(f"Request does not exist. Could not post message: {message}")
    else:
        # Look through messages without clearing them
        msg_list = messages.get_messages(request)
        duplicate_flag = message in [
            m.message for m in msg_list if m.level == msg_level
        ]
        msg_list.used = False

        # If message is a duplicate, do not post it
        if duplicate_flag:
            log_msg = f"[DUPLICATE] {msg}"
        else:
            messages.add_message(request, msg_level, message)
            log_msg = f"[POSTED] {msg}"

        # Always log it (including duplicates)
        if msg_type == "error":
            log.error(log_msg, trace_error=False, strip_html=True)
        elif msg_type == "warning":
            log.warning(log_msg, strip_html=True)
        else:
            log.info(log_msg, strip_html=True)

    return None
