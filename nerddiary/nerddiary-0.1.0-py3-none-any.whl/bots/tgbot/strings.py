def _(text: str):
    return text


# bot.py
CURRENT_VALUE_EMOJI = "✅"
START_REALOD_POLL_REMINDERS = _(
    "Меня перезапускали. Восстанавливаю регулярные напоминания!"
)
START_POLL_REMINDER_SET = _("Буду присылать опрос {} каждый день в {}!")
START_POLL_REMINDER_SET_DESCRIPTION = _("Описание опроса: {}")
START_POLL_COMMAND_DESCRIPTION = _("Начать опрос: {}")
START_NEW_USER_WELCOME = _(
    "Привет! Я - бот дневник. Буду помогать записывать то, что тебе нужно"
)
START_EXISTING_USER_WELCOME = _("Привет! С возвращением!")
USER_ABORT_POLL = _("Ок. Нашел {} опроса(ов) и отменил")
USER_ABORT_NOTHING = _("Ни одного активного опроса в данный момент нет")

ON_DELAY_TEXT = _("Понял. Спрошу еще раз через {} секунд!")

NEW_ROW_FINISHED = _("Спасибо. Вот что получилось:")
NEW_ROW_RECORDING = _("Сохраняю...")
NEW_ROW_RECORDED = _("Супер. Сохранил!")
NEW_ROW_RECORDING_FAILED = _("Не смог сохранить😭 Напишите админу")
NEW_ROW_TIMEDOUT = _("К сожалению прошло слишком много времени и этот опрос отменен")

# admin.py
USER_INVITE_REQUEST = _(
    "Hey! Thanks a lot for your interest in using this bot. At this moment we are in an invite-only mode. I've sent a request to add you to bot administrators. Stay tuned!"
)
USER_INVITE_PENDING = _(
    "Your request is still pending. I'll let you know as soon as ban administrators will approve your request. Sorry for the wait!"
)
USER_INVITE_APPROVED = _(
    "Congrats! Your invitation request was approved by one of the admins. Please press /start"
)
USER_BANNED = _(
    "Oops. One of the administrator banned you from using this bot. I am really sorry. Maybe they had a bad day?"
)
USER_ACTION_PROCESSED = _("Done! User id: {}. Action: {}")
