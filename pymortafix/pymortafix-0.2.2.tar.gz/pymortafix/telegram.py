import sys
import traceback
from datetime import datetime

from colorifix.colorifix import paint
from emoji import emojize

# ---- Utils


def emz(text):
    """emojize everything"""
    if isinstance(text, list):
        return [emz(t) for t in text]
    if isinstance(text, dict):
        return {k: emz(v) for k, v in text.items()}
    return emojize(text, variant="emoji_type")


# ---- Messages


def standard_message(update, top_message, bot_name, bot_url):
    """Build a standard log message"""
    user_name = update.effective_chat.username or update.effective_chat.first_name
    user_id = update.effective_chat.id
    user_mention = f"[{user_name}](tg://user?id={user_id})"
    now = datetime.now()
    return emojize(
        f"{top_message}\n"
        f":robot: [{bot_name}]({bot_url})\n"
        f":calendar: {now:%d.%m.%Y}\n"
        f":eight_o’clock: {now:%H:%M}\n"
        f":bust_in_silhouette: {user_mention} (`{user_id}`)\n"
    )


def send_log(bot, channel, message, document=None):
    """Send a simple message to a channel"""
    if document:
        bot.send_document(
            channel,
            document,
            caption=emojize(message),
            parse_mode="Markdown",
        )
    else:
        bot.send_message(channel, emojize(message), parse_mode="Markdown")


def error_handler(
    update,
    context,
    channel,
    message,
    logger=None,
    exception=None,
    extra_info=None,
    log=True,
):
    """Log an error on terminal and a Telegram channel from a Telegram bot"""
    # error log on terminal
    user_data = context.user_data if update else "None"
    trace = (exception and exception.__traceback__) or sys.exc_info()[2]
    traceback_error = "".join(traceback.format_tb(trace))
    exp = exception or context.error
    traceback_msg = paint(
        f"[#229]{user_data}\n\n[#gray]{traceback_error}" f"[#red]{exp}", False
    )
    if logger:
        logger.warning(traceback_msg)
    else:
        print(traceback_msg)
    # send message to error channel
    if log:
        open("error.log", "w+").write(
            f"{user_data}\n\n"
            f"{extra_info or '...'}\n\n"
            f"{traceback_error}\n"
            f"> {exp}"
        )
        send_log(context.bot, channel, message, open("error.log", "r"))


def not_authorized_handler(update, context, bot_name, bot_url, channel):
    """Log an unauthorized access on a Telegram bot"""
    top_msg = ":face_with_symbols_on_mouth: *NO AUTH USER* :face_with_symbols_on_mouth:"
    message = standard_message(update, top_msg, bot_name, bot_url)
    send_log(context.bot, channel, message)


def sentry_log(project, sentry_url, user):
    """send a telegram log for Sentry"""
    msg = emz(
        f":construction: *{project}* :construction:\n\n"
        f":calendar: {datetime.now():%d.%m.%Y}\n"
        f":bust_in_silhouette: *{user}*\n"
        f":microbe: [Sentry Issue]({sentry_url})"
    )
    return msg
