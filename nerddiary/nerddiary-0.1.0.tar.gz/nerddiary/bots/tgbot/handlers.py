from __future__ import annotations
import datetime
from functools import wraps
import logging
import uuid

from telegram import Update, ChatAction, ReplyKeyboardRemove, ParseMode, Bot, CallbackQuery
from telegram.ext import (  # noqa: F401
    ConversationHandler,
    CallbackContext,
    Dispatcher,
    Job,
)
from telegram.error import Unauthorized, BadRequest
from telegram.ext.jobqueue import JobQueue

from nerddiary.bot.config import BotConfig
from nerddiary.bot.constants import ContextKey, PollState, KeyboardRowSaveCancel
import nerddiary.bot.job as botjob
import nerddiary.bot.strings as BotStrings
from nerddiary.bot.context import (
    ActivePollJobContext,
    JobContext,
    MessageContext,
    NewPollContext,
    NewPollJobContext,
    ActivePollContext,
    ChatContext,
)
from nerddiary.bot.helpers import (
    add_commands_and_handlers,
    generate_buttons,
    log_debug,
    tg_pretty_print_answers,
)
from nerddiary.bot.data import DataConnection
from nerddiary.bot.config import User

from typing import Callable, TYPE_CHECKING, Dict

from nerddiary.bot.workflow import BotWorkflow

if TYPE_CHECKING:
    from nerddiary.bot.admin import BotAdmin

logger = logging.getLogger("nerddiary.bot")


def update_handler(send_typing: bool = False) -> Callable:
    """ Decorator for update handlers: resolves context for message updates, logs debug messages & supports sending typing chat action"""

    def decorator(func):
        @wraps(func)
        def wrapped(
            update: Update, context: CallbackContext, *args, **kwargs
        ) -> str | int | None:

            assert update is not None
            assert context.job is None

            chat_context: ChatContext | None = context.chat_data.get(ContextKey.CHAT_CONTEXT)
            message_context: MessageContext | None = None

            if chat_context:
                message_context = chat_context.active_messages.get(update.effective_message.message_id, None)

            if message_context:
                message_context.from_callback = (
                    True if update.callback_query is not None else False
                )

            # Sending typing action if needed
            if send_typing:
                context.bot.send_chat_action(
                    chat_id=update.effective_message.chat_id, action=ChatAction.TYPING
                )

            # Log all resolved contexts
            logger.debug(
                f"Handler <{func.__name__}>: operating with the following contexts:\n\tChat context: {chat_context}.\n\t\tMessage context: {message_context}."
            )

            result = func(
                update=update,
                context=context,
                chat_context=chat_context,
                message_context=message_context,
            )

            if result and isinstance(result, PollState):
                logger.debug(
                    f"Handler <{func.__name__}> returned new state: {result.name}. Exiting..."
                )
            else:
                logger.debug(f"Handler <{func.__name__}> returned: {result}. Exiting...")

            return result

        return wrapped

    return decorator


def handler(send_typing: bool = False) -> Callable:
    """Decorator for handlers: resolves context for message and job updates, automatically creates or pulls PollContext, logs debug messages & supports sending typing chat action"""

    def decorator(func):
        @wraps(func)
        def wrapped(
            *args, **kwargs
        ) -> str | int | None:

            # case [Update() as update, CallbackContext() as context, ChatContext() as chat_context, ActivePollContext() as active_poll_context, ChatJobContext() as job_context

            update = None
            context = None
            chat_context: ChatContext | None = None
            message_context = None
            job_context = None

            # This match not only handles but also assigns attributes above
            match args:
                # ----------- Handling jobs -----------

                # New poll start job
                case [CallbackContext(job=Job(context=NewPollJobContext(chat_context=_ as chat_context) as job_context)) as context]:
                    logger.debug(
                        f"Processing new poll job using <{func.__name__}> handler, with send_typing set to {str(send_typing)}"
                    )

                # Active poll delay job
                case [CallbackContext(job=Job(context=ActivePollJobContext(active_poll=_ as message_context, chat_context=_ as chat_context) as job_context)) as context]:
                    logger.debug(
                        f"Processing active poll delay job using <{func.__name__}> handler, with send_typing set to {str(send_typing)}"
                    )

                    message_context.from_callback = False

                # ----------- End Handling jobs -----------

                # ----------- Handling updates -----------

                # Same logic for commands, callback_queries and messages
                case [Update() as update, CallbackContext(job=None, chat_data={ContextKey.CHAT_CONTEXT: _ as chat_context}) as context]:
                    logger.debug(
                        f"Processing update using <{func.__name__}> handler, with send_typing set to {str(send_typing)}"
                    )

                    message_context = chat_context.active_messages.get(update.effective_message.message_id, None)

                    if message_context:
                        message_context.from_callback = (
                            True if update.callback_query is not None else False
                        )

                # First message with a user, need to create a chat_context
                case [Update() as update, CallbackContext(job=None, chat_data={}, dispatcher=_ as dp) as context]:
                    chat_id = update.effective_chat.id

                    logger.debug(
                        f"Processing first message with a user <{update.effective_user.username if update.effective_user.username else chat_id}> <{func.__name__}> handler, with send_typing set to {str(send_typing)}"
                    )

                    bot_users: Dict[int, User] = dp.bot_data[ContextKey.BOT_USERS]

                    # Creating context
                    chat_context = ChatContext(
                        chat_id=chat_id,
                        config=bot_users[chat_id],
                        username=update.effective_user.username,
                        job_queue=dp.job_queue,
                    )

                    # Saving context
                    context.chat_data[ContextKey.CHAT_CONTEXT] = chat_context

                    message_context = chat_context.active_messages.get(update.effective_message.message_id, None)

                    if message_context:
                        message_context.from_callback = (
                            True if update.callback_query is not None else False
                        )

                # ----------- End Handling updates -----------

                # ----------- Handling sub handler calls -----------
                # Was called directly with additional context set => skipping processing
                case [Update() as update, CallbackContext() as context, *remainder]:
                    for arg in remainder:
                        if isinstance(arg, MessageContext):
                            message_context = arg
                        if isinstance(arg, ChatContext):
                            chat_context = arg
                        if isinstance(arg, JobContext):
                            job_context = arg

                # ----------- End Handling sub handler calls -----------
                case _:
                    raise NotImplementedError(f"Unknown context passed to handler <{func.__name__}>")

            # Sending typing action if needed
            if send_typing:
                context.bot.send_chat_action(
                    chat_id=update.effective_message.chat_id, action=ChatAction.TYPING
                )

            # Log all resolved contexts
            logger.debug(
                f"Handler <{func.__name__}>: operating with the following contexts:\n\tChat context: {chat_context}.\n\t\tMessage context: {message_context}.\n\tJob context: {job_context}."
            )

            result = func(
                update=update,
                context=context,
                chat_context=chat_context,
                message_context=message_context,
                job_context=job_context,
            )

            if result and isinstance(result, PollState):
                logger.debug(
                    f"Handler <{func.__name__}> returned new state: {result.name}. Exiting..."
                )
            else:
                logger.debug(f"Handler <{func.__name__}> returned: {result}. Exiting...")

            return result

        return wrapped

    return decorator


@handler()
def process_select(
    update: Update,
    context: CallbackContext,
    chat_context: ChatContext,
    message_context: MessageContext,
    job_context: JobContext,
    *args,
    **kwargs,
) -> int | str | None:
    """Checks select value and stores it"""

    workflow = None
    active_poll_context = None

    # Matching and capturing within match patterns when possible
    match [update, job_context, message_context]:
        # One of the questions in between
        case [Update(callback_query=CallbackQuery()), None, ActivePollContext(poll_workflow=BotWorkflow(started=True) as workflow) as active_poll_context]:
            # Prevent processing duplicate clicks
            if update.callback_query.data not in workflow.get_select():
                logger.warn(
                    "Callback was called with callback data that is not matching the current question. Probably double-tap. Skipping"
                )

                return None
        # Some other update not intended for this conversation
        case [Update(), None, MessageContext()]:
            return None
        case _:
            raise NotImplementedError("Unknown context passed to `process_select`")

    not_delayed = active_poll_context.poll_workflow.add_answer(
        update.callback_query.data
    )

    if not_delayed:
        return ask_next_value(
            update,
            context,
            chat_context,
            active_poll_context,
            job_context,
        )
    else:
        # Delay
        delay_time = active_poll_context.poll_workflow.get_delay_time()
        text = BotStrings.ON_DELAY_TEXT.format(str(delay_time.seconds))
        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text, parse_mode=ParseMode.HTML)

        if not job_context:
            job_context = ActivePollJobContext(
                chat_context=chat_context,
                job_name=str(uuid.uuid4()),
                active_poll=active_poll_context,
            )

        active_poll_context.delay_job_context = job_context  # type: ignore

        botjob.run_once(
            callback=ask_next_value,
            job_queue=chat_context.job_queue,
            job_context=job_context,
            when=delay_time,
        )

        return None


@handler(send_typing=True)
def confirm_row(
    update: Update,
    context: CallbackContext,
    chat_context: ChatContext,
    message_context: MessageContext,
    job_context: JobContext,
    *args,
    **kwargs,
) -> int | str | None:
    """If user confirmed the row - add it, otherwise restart"""

    # Check row is being processed already
    if not isinstance(message_context, ActivePollContext):
        raise ValueError(
            "Handler <confirm_row> called out of order - current row is not set"
        )

    if update.callback_query.data == KeyboardRowSaveCancel.BUTTON_CONFIRM_ROW[0]:
        # Prepare reply
        original_text = update.callback_query.message.text_html.split("\n")
        del original_text[0]
        text = BotStrings.NEW_ROW_RECORDING + "\n" + "\n".join(original_text)
        keyboard = None

        update.callback_query.answer()
        update.callback_query.edit_message_text(
            text=text, reply_markup=keyboard, parse_mode=ParseMode.HTML
        )

        # Commit row
        dpr: DataConnection = chat_context.data_connection

        result = dpr.append_log(message_context.poll_key, message_context.poll_workflow.get_save_data())

        # Prepare reply
        if result:
            chat_context.poll_last_timestamps[message_context.poll_key] = message_context.poll_workflow.poll_start_timestamp

            text = BotStrings.NEW_ROW_RECORDED + "\n" + "\n".join(original_text)
        else:
            text = BotStrings.NEW_ROW_RECORDING_FAILED + "\n" + "\n".join(original_text)

        update.callback_query.edit_message_text(
            text=text, reply_markup=keyboard, parse_mode=ParseMode.HTML
        )

        # Clear up current record context
        del chat_context.active_messages[message_context.message_id]

        return ConversationHandler.END
    else:
        message_context.reset_workflow()
        return ask_next_value(
            update,
            context,
            chat_context,
            message_context,
            job_context
        )


@handler()
def timeout(
    update: Update,
    context: CallbackContext,
    chat_context: ChatContext,
    message_context: MessageContext,
    job_context: JobContext,
    *args,
    **kwargs,
) -> int | None:
    if not isinstance(message_context, ActivePollContext):
        return None

    # If it timed out because it was previously cancelled - just close conversation
    if message_context.cancelled:
        return ConversationHandler.END

    # Prepare reply
    if update.callback_query:
        original_text = update.effective_message.text_html.split("\n")
    elif update.message:
        original_text = update.message.text_html.split("\n")
    else:
        original_text = ["del"]

    del original_text[0]
    text = BotStrings.NEW_ROW_TIMEDOUT + "\n" + "\n".join(original_text)

    context.bot.edit_message_text(
        text=text, chat_id=chat_context.chat_id, message_id=message_context.message_id, reply_markup=None
    )
    # Clear up current record context
    del chat_context.active_messages[message_context.message_id]

    if message_context.delay_job_context:
        botjob.dispose_chat_job(
            context.job_queue, message_context.delay_job_context  # type: ignore
        )

    return ConversationHandler.END


@handler()
def cancel(
    update: Update,
    context: CallbackContext,
    chat_context: ChatContext,
    message_context: MessageContext,
    job_context: JobContext,
    *args,
    **kwargs,
) -> int:
    count = 0
    delayed_remove = []
    for message, act_poll in chat_context.active_messages.items():
        if isinstance(act_poll, ActivePollContext):
            count += 1
            context.bot.delete_message(
                chat_id=chat_context.chat_id,
                message_id=message,
            )

            act_poll.cancelled = True

            delayed_remove.append(message)

    if count > 0:
        for mes in delayed_remove:
            # Clear up current record context
            del chat_context.active_messages[mes]

        context.bot.send_message(
            text=BotStrings.USER_ABORT_POLL.format(count),
            chat_id=chat_context.chat_id,
        )
    else:
        context.bot.send_message(
            text=BotStrings.USER_ABORT_NOTHING.format(count),
            chat_id=chat_context.chat_id,
        )

    return ConversationHandler.END


@handler()
def ask_next_value(
    *args,
    **kwargs,
) -> int | str | None:
    """Iterates through values to be set."""

    text = ""
    keyboard = None
    ret = None
    workflow = None
    active_poll_context = None
    message_id = None
    poll_key = None
    poll_config = None

    # HACK: this one is scheduled and APScheduler checks signatures. It is not accounting for handler decorator that resolves all missing parameters
    update = kwargs["update"]
    context: CallbackContext = kwargs["context"]
    chat_context: ChatContext = kwargs["chat_context"]
    message_context = kwargs["message_context"]
    job_context = kwargs["job_context"]

    # Matching and capturing within match patterns when possible
    match [update, job_context, message_context]:
        # New poll starting from job
        case [None, NewPollJobContext(poll_key=_ as poll_key) as job_context, None]:
            poll_config = chat_context.config.polls[poll_key]

            # If this poll is only recorded once per day and we already have a record for today - stop. Applying the same hour correction logic
            if poll_config.once_per_day:
                user_timezone = chat_context.config.timezone
                adjusted_date = None
                if poll_config.hours_over_midgnight:
                    now = datetime.datetime.now(user_timezone)
                    check = now - datetime.timedelta(hours=poll_config.hours_over_midgnight)
                    if check.date() < now.date():
                        adjusted_date = check
                    else:
                        adjusted_date = now

                last_timestamp = chat_context.poll_last_timestamps.get(poll_key, None)
                if last_timestamp and last_timestamp.date() == adjusted_date.date():
                    return None

            workflow = BotWorkflow(
                poll_config, chat_context.config
            )
        # From delay
        case [None, ActivePollJobContext() as job_context, ActivePollContext(message_id=_ as message_id, poll_workflow=BotWorkflow() as workflow) as active_poll_context]:
            pass
        # From re-starting the poll (`confirm_row`)
        case [Update(), None, ActivePollContext(message_id=_ as message_id, poll_workflow=BotWorkflow(started=False) as workflow) as active_poll_context]:
            pass
        # New poll starting from command
        case [Update(), None, NewPollContext(poll_key=_ as poll_key)]:
            poll_config = chat_context.config.polls[poll_key]
            workflow = BotWorkflow(
                poll_config, chat_context.config
            )
        # One of the questions in between
        case [Update(callback_query=CallbackQuery()), None, ActivePollContext(message_id=_ as message_id, poll_workflow=BotWorkflow(started=True) as workflow) as active_poll_context]:
            # Prevent processing duplicate clicks
            if update.callback_query.data not in workflow.get_select():
                logger.warn(
                    "Callback was called with callback data that is not matching the current question. Probably double-tap. Skipping"
                )

                return None
        # Some other update not intended for this conversation
        case [Update(), None, MessageContext()]:
            return None
        case _:
            raise NotImplementedError("Unknown context passed to `ask_next_value`")

    next_question = workflow.get_next_question()

    if workflow.all_set:
        text = BotStrings.NEW_ROW_FINISHED
        text += "\n" + tg_pretty_print_answers(
            questions=workflow.questions, answers=workflow.answers
        )

        keyboard = generate_buttons(
            [
                KeyboardRowSaveCancel.BUTTON_CONFIRM_ROW,
                KeyboardRowSaveCancel.BUTTON_CANCEL_ROW,
            ]
        )
        ret = PollState.CONFIRMING_ROW
    else:
        text = next_question

        keyboard = generate_buttons(workflow.get_select())
        ret = PollState.CHOOSING_SELECT_VALUE

    # New poll, no message yet. From job
    if not message_id:
        msg = context.bot.send_message(
            chat_id=chat_context.chat_id,
            text=text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML,
        )

        message_id = msg.message_id
        # Create context. It will attach itself to the list of active message context for chat_context automatically
        active_poll_context = ActivePollContext(chat_context, True, message_id, poll_key, poll_config, workflow)  # type: ignore

    # Regular message in between
    elif active_poll_context.from_callback:
        update.callback_query.answer()
        update.callback_query.edit_message_text(
            text=text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML,
        )

    # From delay - removing old message and starting a new
    elif job_context:
        context.bot.delete_message(
            chat_id=chat_context.chat_id,
            message_id=message_id,
        )

        msg = context.bot.send_message(
            chat_id=chat_context.chat_id,
            text=text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML,
        )

        message_id = msg.message_id
        active_poll_context.replace_message(message_id)

    # New poll, no message yet. From command
    else:
        msg = update.message.reply_text(
            text, reply_markup=keyboard, parse_mode=ParseMode.HTML
        )

        message_id = msg.message_id

        # Create context. It will attach itself to the list of active message context for chat_context automatically
        active_poll_context = ActivePollContext(chat_context, True, message_id, poll_key, poll_config, workflow)  # type: ignore

    return ret


@update_handler()
def start(
    update: Update,
    context: CallbackContext,
    chat_context: ChatContext,
    message_context: MessageContext
) -> None:
    logger.debug(
        f"Processing start command for user id: {update.effective_user.id}; user name: {update.effective_user.username} "
    )

    dp: Dispatcher = context.dispatcher

    # First message after bot start/restart
    if ChatContext is None:
        chat_id = update.effective_chat.id

        bot_users: Dict[int, User] = dp.bot_data[ContextKey.BOT_USERS]
        if chat_id not in bot_users:
            NotImplementedError("Bot doesn't support new users without configs")

        user = bot_users[chat_id]
        if user.encrypt_data:
            msg = update.message.reply_text(
                text, reply_markup=keyboard, parse_mode=ParseMode.HTML
            )
        else:
            # No encryption, can create context & schedule jobs right away
            text = ""
            bot_config: BotConfig = dp.bot_data[ContextKey.BOT_CONFIG]

            # New user, first ever message
            if not bot_config._data_provider.check_data_exist(user):
                text = BotStrings.START_NEW_USER_WELCOME
            # Existing user
            else:
                text = BotStrings.START_EXISTING_USER_WELCOME

            update.message.reply_text(
                text, reply_markup=None
            )

            chat_context = ChatContext(
                chat_id=chat_id,
                config=bot_users[chat_id],
                username=update.effective_user.username,
                job_queue=dp.job_queue,
                data_connection=bot_config._data_provider.get_connection(user)
            )

            context.chat_data[ContextKey.CHAT_CONTEXT] = chat_context

            reload_user_jobs(user=user, bot_config=bot_config, dp=dp, chat_context=chat_context)

    # Currently active user (repeat start command)
    else:
        pass

    """ Add a job to the queue. """
    assert context.job_queue

    reload_user_poll_jobs(
        from_start_command=True,
        config=chat_context.config,
        bot_config=context.bot_data[ContextKey.BOT_CONFIG],
        bot=context.bot,
        dp=context.dispatcher,
        chat_context=chat_context,
        job_queue=context.job_queue,
    )


@log_debug(logger)
def reload_user_poll_jobs(
    from_start_command: bool,
    config: User,
    bot_config: BotConfig,
    bot: Bot,
    dp: Dispatcher,
    chat_context: ChatContext | None,
    job_queue: JobQueue,
) -> None:
    username = None

    if not config.polls:
        # If no polls defined, do nothing
        return

    if not from_start_command:
        # If this is a bot reload, we must check that bot is allowed to chat with the user before proceeding

        try:
            text = BotStrings.START_REALOD_POLL_REMINDERS

            message = bot.send_message(
                chat_id=config.id, text=text, reply_markup=ReplyKeyboardRemove()
            )

            username = message.chat.username
        except Unauthorized:
            return
        except BadRequest:
            return

    commands = []

    for key, poll in config.polls.items():
        # Adding user commands for manually starting poll
        if poll.command:
            commands.append(
                (
                    poll.command,
                    BotStrings.START_POLL_COMMAND_DESCRIPTION.format(poll.description if poll.description else poll.poll_name),
                    start_poll,
                )
            )

        if poll.reminder_time:
            if not chat_context:
                # Called without a chat context, trying to find existing context
                chat_data = dp.chat_data.get(config.id, None)
                if chat_data:
                    chat_context = chat_data.get(
                        ContextKey.CHAT_CONTEXT,
                        ChatContext(
                            chat_id=config.id,
                            config=config,
                            username=username,
                            job_queue=job_queue,
                        ),
                    )
                else:
                    chat_context = ChatContext(
                        chat_id=config.id,
                        config=config,
                        username=username,
                        job_queue=job_queue,
                    )

                    # Save newly created context
                    dp.chat_data[config.id] = {ContextKey.CHAT_CONTEXT: chat_context}

            job_context = NewPollJobContext(
                chat_context=chat_context,  # type: ignore
                job_name=key,
                poll_key=key,
            )

            botjob.remove_jobs(job_queue=job_queue, job_context=job_context)

            if bot_config.bot_debug:
                botjob.run_daily(
                    callback=ask_next_value,
                    job_queue=job_queue,
                    job_context=job_context,
                    time=(
                        datetime.datetime.now(config.timezone) + datetime.timedelta(seconds=60)
                    ).time().replace(tzinfo=config.timezone),
                )
            else:
                botjob.run_daily(
                    callback=ask_next_value,
                    job_queue=job_queue,
                    job_context=job_context,
                    time=poll.reminder_time,
                )

            text = BotStrings.START_POLL_REMINDER_SET.format(
                poll.poll_name,
                str(poll.reminder_time),
            )

            if poll.description:
                text += "\n\n" + BotStrings.START_POLL_REMINDER_SET_DESCRIPTION.format(
                    poll.description
                )

            bot.send_message(chat_id=config.id, text=text)

    if commands and not add_commands_and_handlers(config.id, dp, commands):
        raise RuntimeError(f"Failed to add commands for user {config.id}")


@log_debug(logger)
def reload_user_jobs(
    user: User,
    bot_config: BotConfig,
    dp: Dispatcher,
    chat_context: ChatContext,
) -> None:
    if not user.polls:
        # If no polls defined, do nothing
        return

    commands = []

    for key, poll in user.polls.items():
        # Adding user commands for manually starting poll
        if poll.command:
            commands.append(
                (
                    poll.command,
                    BotStrings.START_POLL_COMMAND_DESCRIPTION.format(poll.description if poll.description else poll.poll_name),
                    start_poll,
                )
            )

        if poll.reminder_time:

            job_context = NewPollJobContext(
                chat_context=chat_context,  # type: ignore
                job_name=key,
                poll_key=key,
            )

            botjob.remove_jobs(job_queue=dp.job_queue, job_context=job_context)

            if bot_config.bot_debug:
                botjob.run_daily(
                    callback=ask_next_value,
                    job_queue=dp.job_queue,
                    job_context=job_context,
                    time=(
                        datetime.datetime.now(user.timezone) + datetime.timedelta(seconds=10)
                    ).time().replace(tzinfo=user.timezone),
                )
            else:
                botjob.run_daily(
                    callback=ask_next_value,
                    job_queue=dp.job_queue,
                    job_context=job_context,
                    time=poll.reminder_time,
                )

            text = BotStrings.START_POLL_REMINDER_SET.format(
                poll.poll_name,
                str(poll.reminder_time),
            )

            if poll.description:
                text += "\n\n" + BotStrings.START_POLL_REMINDER_SET_DESCRIPTION.format(
                    poll.description
                )

            dp.bot.send_message(chat_id=user.id, text=text)

    if commands and not add_commands_and_handlers(user.id, dp, commands):
        raise RuntimeError(f"Failed to add commands for user {user.id}")


@handler()
def start_poll(
    update: Update,
    context: CallbackContext,
    chat_context: ChatContext,
    message_context: MessageContext,
    job_context: JobContext,
    *args,
    **kwargs,
) -> int | str | None:
    """Initiates new poll."""

    command = update.effective_message.text[1:]

    for key, poll in chat_context.config.polls.items():
        if poll.command == command:
            message_context = NewPollContext(
                chat_context=chat_context,
                from_callback=False,
                message_id=update.effective_message.message_id,
                poll_key=key,
            )

            return ask_next_value(update, context, chat_context, message_context, job_context)

    raise ValueError("Got a start poll command for non existing poll")


def handle_error(
    update: Update,
    context: CallbackContext,
) -> None:

    """Log the error and send a telegram message to notify the admin."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    if isinstance(update, Update):
        if update.effective_user.link:
            message = f"An exception was raised while handling an update from <a href='{update.effective_user.link}'>{update.effective_user.username}</a>"
        else:
            message = f"An exception was raised while handling an update from chat id: {update.effective_user.id}"
    else:
        message = "An exception was raised while handling system update"

    # Finally, send the message if not live debugging
    bot_config: BotConfig = context.dispatcher.bot_data[ContextKey.BOT_CONFIG]
    if not bot_config.bot_debug:

        ba: BotAdmin = context.bot_data.get(ContextKey.BOT_ADMIN, None)

        if ba:
            ba._send_message_to_admin(
                context=context,
                text=message,
                parse_mode=ParseMode.HTML,
            )
    else:
        assert isinstance(context.error, Exception)
        raise context.error
