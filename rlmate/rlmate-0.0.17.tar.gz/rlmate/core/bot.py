import logging
import threading

try:
    from telegram.ext import Updater
    from telegram import Bot, User
    from telegram.ext import CommandHandler
    from telegram.error import (
        TelegramError,
        Unauthorized,
        BadRequest,
        TimedOut,
        ChatMigrated,
        NetworkError,
    )
except ModuleNotFoundError:
    logging.warning(
        "Module telegram was not found, attempting to use any telegram messaging features will break."
    )

import git


def kill_updater(updater):
    updater.stop()
    updater.is_idle = False


class Bot_handler:
    def __init__(self):
        git_repo = git.Repo("./", search_parent_directories=True)
        git_root = git_repo.git.rev_parse("--show-toplevel")

        bot_id = None
        chat_ids = []
        with open(git_root + "/.hermes_settings", "r") as f:
            for line in f:

                if line.startswith("bot_id"):
                    assert bot_id == None, "You can only specify ony bot_id"
                    bot_id = line[7:].replace("\n", "")

                if line.startswith("chat_id"):
                    chat_id = line[8:].replace("\n", "")
                    chat_ids.append(chat_id)

        assert bot_id != None, "you need to specify a bot to send telegram messages"
        if chat_ids == []:
            logging.warning("No chat id was specified. No messages will be sent")

        self.bot_id = bot_id
        self.chat_ids = chat_ids

        self.bot = Bot(self.bot_id)

    def message(self, text):
        for chat_id in self.chat_ids:
            self.bot.send_message(chat_id=chat_id, text=text)

    def picture(self, path="tmp.png", caption=""):
        for chat_id in self.chat_ids:
            self.bot.send_photo(chat_id, photo=open(path, "rb"), caption=caption)

    def register(self):
        updater = Updater(token=self.bot_id)

        def start(update, callback):
            message_id = update.message.chat.id
            res = "Your chat_id is " + str(message_id) + ", please add the line\n"
            res += "chat_id=" + str(message_id)
            res += "\nto your .hermes_settings file"
            update.message.reply_text(res)
            t = threading.Thread(name="killer", target=kill_updater, args=(updater,))
            t.start()

        start_handler = CommandHandler("start", start)
        dispatcher = updater.dispatcher
        dispatcher.add_handler(start_handler)
        updater.start_polling()
