""" This module contains administration related classes, handlers and functions
"""
from __future__ import annotations
from functools import wraps
import os
import sys
import logging
from threading import Thread
from typing import List, Optional

from telegram import Update
from telegram.error import Unauthorized
from telegram.ext import (
    CallbackContext,
    Updater,
    TypeHandler,
    CallbackQueryHandler,
    DispatcherHandlerStop,
    Dispatcher,
)
from telegram.replymarkup import ReplyMarkup

from nerddiary.bot.config import BotConfig
from nerddiary.bot.model import User
from nerddiary.bot.constants import ContextKey, KeyboardAdminModerate, HandlerGroup
import nerddiary.bot.strings as BotStrings
from nerddiary.bot.helpers import generate_buttons, add_commands_and_handlers
import nerddiary.bot.handlers as bot_handlers

logger = logging.getLogger("nerddiary.bot.admin")


def admin_handler_method(func):
    """Checks whether user is an admin before executing handler callback"""

    @wraps(func)
    def wrapped(
        self, update: Update, context: CallbackContext, *args, **kwargs
    ) -> Optional[str]:
        user_id = update.effective_user.id
        admin_list = context.bot_data[ContextKey.BOT_ADMIN].admin_list
        if user_id not in admin_list:
            logger.info(
                f"Unauthorized access for message text: '{update.message.text}' was denied for user id: '{user_id}', username: {update.effective_user.username}."
            )
            return
        return func(self, update, context, *args, **kwargs)

    return wrapped


class BotAdmin:
    def __new__(cls, updater: Updater, *args, **kwargs) -> BotAdmin:
        dp = updater.dispatcher

        # Save admin object to bot data
        instance = dp.bot_data.get(ContextKey.BOT_ADMIN, None)

        if instance is not None:
            return instance

        return super().__new__(cls)

    def __init__(
        self,
        updater: Updater,
        allow_list_only: bool = True,
        allow_list: List[int] = [],
        admin_list: List[int] = [],
        add_invite_handler: bool = False,
        add_restart_command: bool = False,
    ) -> None:
        """
        Special class that defines various handlers and helper decorators.

        Args:
            add_restart_handler: bool = False - Adds a handler for /adm_restart command to gracefully stop the Updater and replace the current process with a new one
        """

        self._updater = updater
        self._ban_list: List[int] = []
        self._allow_list: List[int] = allow_list
        self._pending_list: List[int] = []
        self._admin_list: List[int] = admin_list if admin_list is not None else []

        dp: Dispatcher = updater.dispatcher

        # Save admin object to bot data
        dp.bot_data[ContextKey.BOT_ADMIN] = self

        # Add admin only bot commands
        if self.admin_list:
            for adm_chat_id in self.admin_list:
                self._add_admin_commands(
                    adm_chat_id, dp, add_restart_command=add_restart_command
                )

        # if invite system is `on` - handle user id checks first
        if add_invite_handler is True:
            dp.add_handler(
                CallbackQueryHandler(
                    self._process_admin_user_action,
                    pattern=f"^({str(KeyboardAdminModerate.BUTTON_ADMIN_ALLOW[0])}|{str(KeyboardAdminModerate.BUTTON_ADMIN_BAN[0])}|{str(KeyboardAdminModerate.BUTTON_ADMIN_DONOTHING[0])})$",
                ),
                group=HandlerGroup.SPAM_CONTROL,
            )

            dp.add_handler(
                TypeHandler(Update, self._check_user_invite),
                group=HandlerGroup.SPAM_CONTROL,
            )
        # If allow list given, check for it
        elif allow_list_only and self.allow_list:
            dp.add_handler(
                TypeHandler(Update, self._check_allow_list),
                group=HandlerGroup.SPAM_CONTROL,
            )
        # At minimum prevent banned user updates
        else:
            dp.add_handler(
                TypeHandler(Update, self._check_ban_list),
                group=HandlerGroup.SPAM_CONTROL,
            )

        super(BotAdmin, self).__init__()

    @property
    def admin_list(self) -> List[int]:
        """Returns list of bot admins"""
        return self._admin_list

    @property
    def ban_list(self) -> List[int]:
        """Returns list of banned user ids"""
        return self._ban_list

    @property
    def allow_list(self) -> List[int]:
        """Returns list of allowed (invited) user ids"""
        return self._allow_list

    @property
    def pending_list(self) -> List[int]:
        """Returns list of pending invite user ids"""
        return self._pending_list

    def _stop_and_restart(self):
        """Gracefully stop the Updater and replace the current process with a new one"""
        self._updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def _add_admin_commands(
        self, chat_id: int, dp: Dispatcher, add_restart_command: bool = False
    ) -> None:
        commands = []

        # add config reload command & handler
        commands.append(
            (
                "reload",
                "CAUTION! Reload config and reset reminders",
                self._reload_handler,
            )
        )

        # add restart handler & command
        if add_restart_command:
            commands.append(("restart", "CAUTION! Restarts bot", self._restart))

        if not add_commands_and_handlers(chat_id, dp, commands, HandlerGroup.ADMIN):
            raise RuntimeError("Failed to add admin commands")

    # TODO: test restart in prod mode
    @admin_handler_method
    def _restart(self, update: Update, context: CallbackContext) -> Optional[str]:
        update.message.reply_text("Bot is restarting...")
        Thread(target=self._stop_and_restart).start()

    def _check_user_invite(
        self, update: Update, context: CallbackContext
    ) -> Optional[str]:
        """Checks whether user id is among admins or invited, requests invite if neither. Also stops message handling for banned users"""
        # Get current user id
        user_id = update.effective_user.id

        # Get admin list
        admin_list = context.bot_data[ContextKey.BOT_ADMIN].admin_list
        # If user is an admin - proceed
        if user_id in admin_list:
            return

        # Get ban list
        ban_list = context.bot_data[ContextKey.BOT_ADMIN].ban_list
        # If user is banned stop all handlers
        if user_id in ban_list:
            raise DispatcherHandlerStop()

        # Get pending list
        pending_list = context.bot_data[ContextKey.BOT_ADMIN].pending_list
        # If user is pending, remind them and stop all handlers
        if user_id in pending_list:
            # TODO: Add translation using tg user language code param
            text = BotStrings.USER_INVITE_PENDING
            update.message.reply_text(text)

            raise DispatcherHandlerStop()

        # Get allow list
        allow_list = context.bot_data[ContextKey.BOT_ADMIN].allow_list
        # If user is banned stop all handlers
        if user_id not in allow_list:
            # TODO: Add translation using tg user language code param
            text = BotStrings.USER_INVITE_REQUEST
            update.message.reply_text(text)

            # TODO: user_ids need to be stored in a queque alongside message ids, in case admin recieves multiple requests before confirming
            context.bot_data[ContextKey.BOT_ADMIN_USER_ACTION] = user_id
            text = f"Invitation request. user id: {user_id}; username: {update.effective_user.username}; first and last name: {update.effective_user.first_name} {update.effective_user.last_name}"
            keyboard = generate_buttons(
                [
                    KeyboardAdminModerate.BUTTON_ADMIN_ALLOW,
                    KeyboardAdminModerate.BUTTON_ADMIN_BAN,
                    KeyboardAdminModerate.BUTTON_ADMIN_DONOTHING,
                ]
            )

            self._send_message_to_admin(
                context=context, text=text, reply_markup=keyboard
            )

            raise DispatcherHandlerStop()

    @admin_handler_method
    def _process_admin_user_action(
        self, update: Update, context: CallbackContext
    ) -> Optional[str]:
        """Process admin repsonse for user approval request"""
        admin_action = update.callback_query.data
        user_id = context.bot_data.get(ContextKey.BOT_ADMIN_USER_ACTION, None)

        if user_id is not None:
            if admin_action == KeyboardAdminModerate.BUTTON_ADMIN_ALLOW[0]:
                self._allow_list.append(user_id)
                self._pending_list.remove(user_id)

                # TODO: Add translation using tg user language code param
                text = BotStrings.USER_INVITE_APPROVED
                try:
                    context.bot.send_message(chat_id=user_id, text=text)
                    pass
                except Unauthorized:
                    self._allow_list.remove(user_id)

                action = KeyboardAdminModerate.BUTTON_ADMIN_ALLOW[1]
            elif admin_action == KeyboardAdminModerate.BUTTON_ADMIN_BAN[0]:
                self._ban_list.append(user_id)
                self._pending_list.remove(user_id)
                text = BotStrings.USER_BANNED
                try:
                    context.bot.send_message(chat_id=user_id, text=text)
                except Unauthorized:
                    pass

                action = KeyboardAdminModerate.BUTTON_ADMIN_BAN[1]
            else:
                action = KeyboardAdminModerate.BUTTON_ADMIN_DONOTHING[1]

            update.callback_query.answer()
            update.callback_query.edit_message_text(
                text=BotStrings.USER_ACTION_PROCESSED.format(str(user_id), action),
                reply_markup=None,
            )

        context.bot_data[ContextKey.BOT_ADMIN_USER_ACTION] = None

    @admin_handler_method
    def _reload_handler(
        self, update: Update, context: CallbackContext
    ) -> Optional[str]:
        """Reload config from admin command"""

        self._send_message_to_admin(
            context=context,
            text=f"Caution! Admin <{update.effective_user.username}> initiated config reloading ",
        )

        dp = context.dispatcher

        # Load config
        dp.bot_data[ContextKey.BOT_CONFIG] = bot_config = BotConfig.load_config()

        # Reset admin list
        self._admin_list = bot_config.admins

        dp.bot_data[ContextKey.BOT_USERS] = bot_users = User.from_folder(
            bot_config.user_conf_path.name,
            bot_config.default_timezone,
            bot_config.question_types,
        )

        # Reset allow_list
        self._allow_list = [user for user in bot_users]

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

        self._send_message_to_admin(
            context=context,
            text=f"Reloaded bot config.\nThis is the current list of admins: {str(bot_config.admins)}",
        )

    def _check_ban_list(
        self, update: Update, context: CallbackContext
    ) -> Optional[str]:
        """Stops message handling for banned users"""

        # Get current user id
        user_id = update.effective_user.id
        # Get ban list
        ban_list = context.bot_data[ContextKey.BOT_ADMIN].ban_list

        # If user is banned stop all handlers
        if user_id in ban_list:
            raise DispatcherHandlerStop()

    def _check_allow_list(
        self, update: Update, context: CallbackContext
    ) -> Optional[str]:
        """Stops message handling for everyone except allowed users"""

        # Get current user id
        user_id = update.effective_user.id

        # Get admin list
        admin_list = context.bot_data[ContextKey.BOT_ADMIN].admin_list
        # If user is an admin - proceed
        if user_id in admin_list:
            return

        # Get ban list
        allow_list = context.bot_data[ContextKey.BOT_ADMIN].allow_list

        # If user is not allowed stop all handlers
        if user_id not in allow_list:
            raise DispatcherHandlerStop()

    def _send_message_to_admin(
        self,
        context: CallbackContext,
        text: str,
        reply_markup: ReplyMarkup = None,
        parse_mode: str = None,
    ) -> None:
        if self.admin_list:
            for admin in self.admin_list:
                context.bot.send_message(
                    chat_id=admin, text=text, reply_markup=reply_markup
                )

    @classmethod
    def send_message_to_admin(
        cls,
        context: CallbackContext,
        text: str,
        reply_markup: ReplyMarkup = None,
        parse_mode: str = None,
    ) -> None:
        ba: BotAdmin = context.bot_data.get(ContextKey.BOT_ADMIN, None)

        if ba:
            ba._send_message_to_admin(
                context=context,
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
            )
