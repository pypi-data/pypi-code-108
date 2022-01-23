import logging

from telegram import Update
from telegram.ext import (  # noqa: F401
    Updater,
    CommandHandler,
    TypeHandler,
    ConversationHandler,
    CallbackQueryHandler,
)
from telegram.ext.dispatcher import Dispatcher

from nerddiary.bot.constants import ContextKey, HandlerGroup, PollState
from nerddiary.bot.admin import BotAdmin
import nerddiary.bot.handlers as bot_handlers
from nerddiary.bot.config import BotConfig
from nerddiary.bot.model import User

logger = logging.getLogger("nerddiary.bot")


def main(bot_token, config_file, gsheet_api_wrapper):

    # Create the Updater and pass it your bot's token.
    updater = Updater(bot_token)

    # Get the dispatcher to register handlers
    dp: Dispatcher = updater.dispatcher

    # Load config
    dp.bot_data[ContextKey.BOT_CONFIG] = bot_config = BotConfig.load_config(config_file)

    dp.bot_data[ContextKey.BOT_USERS] = bot_users = User.from_folder(
        bot_config.user_conf_path.name,
        bot_config.default_timezone,
        bot_config.question_types,
    )

    # Init all admin handlers and functions (BotAdmin adds itself to bot_date)
    allow_list = [user for user in bot_users]
    BotAdmin(
        updater,
        allow_list=allow_list,
        allow_list_only=True,
        admin_list=bot_config.admins,
    )

    # Add basic start handler
    dp.add_handler(
        CommandHandler("start", bot_handlers.start), HandlerGroup.BASE  # type: ignore
    )

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(bot_handlers.process_select)],  # type: ignore
        states={
            PollState.CONFIRMING_ROW: [
                CallbackQueryHandler(bot_handlers.confirm_row),  # type: ignore
            ],
            PollState.CHOOSING_SELECT_VALUE: [
                CallbackQueryHandler(bot_handlers.process_select),  # type: ignore
            ],
            ConversationHandler.TIMEOUT: [TypeHandler(Update, bot_handlers.timeout)],  # type: ignore
        },
        fallbacks=[],
        name="poll_handler",
        conversation_timeout=bot_config.conversation_timeout,
        per_message=True,
    )

    dp.add_handler(conv_handler, group=HandlerGroup.COONVERSATION)

    # Add global handler to cancel all active polls
    dp.add_handler(
        CommandHandler("cancel", bot_handlers.cancel),  # type: ignore
        group=HandlerGroup.BASE,
    )

    # Add error handler
    dp.add_error_handler(bot_handlers.handle_error)  # type: ignore

    # show_data_handler = CommandHandler('show_data', show_data)
    # dp.add_handler(show_data_handler)
    logger.debug(
        f"Starting bot with the following config: {str(bot_config)}.\nWith this admins: {str(bot_config.admins)}"
    )

    # Start the Bot
    updater.start_polling()

    # Reload reminders from config where possible
    for user_config in bot_users.values():
        bot_handlers.reload_user_poll_jobs(
            from_start_command=False,
            config=user_config,
            bot_config=bot_config,
            bot=dp.bot,
            dp=dp,
            chat_context=None,
            job_queue=dp.job_queue,
        )

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    pass
