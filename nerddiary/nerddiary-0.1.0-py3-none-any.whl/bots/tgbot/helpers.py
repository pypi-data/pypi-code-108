""" This module contains utility functions used by multiple tgjournalbot paretn package modules """
from __future__ import annotations
import html
import enum
from functools import wraps

from nerddiary.bot.constants import MAX_INLINE_KEYBOARD_ROW_BUTTONS, HandlerGroup
import nerddiary.bot.strings as BotStrings

from telegram import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    BotCommand,
    BotCommandScopeChat,
    Bot,
)
from telegram.ext import Dispatcher, CommandHandler

from typing import Callable, Optional, List, Tuple, Union, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from nerddiary.bot.model import Question, ValueLabel


def add_commands_and_handlers(
    chat_id: int,
    dp: Dispatcher,
    commands: List[Tuple[str, str, Callable]],
    handler_group: HandlerGroup = HandlerGroup.BASE,
) -> bool:
    scope = BotCommandScopeChat(chat_id=chat_id)

    bot: Bot = dp.bot

    # Get default commands for this admin
    default_commands = bot.get_my_commands()
    # Add current commands for this admin
    current_commands = bot.get_my_commands(scope=scope) + default_commands

    for command, desc, handler in commands:
        current_commands.append(BotCommand(command, desc))

        dp.add_handler(CommandHandler(command, handler), group=handler_group)

    return bot.set_my_commands(commands=current_commands, scope=scope)


def tg_pretty_print_answers(
    questions: Dict[str, Question],
    answers: List[ValueLabel],
) -> str:
    print_questions = [n for n, q in questions.items() if not q.ephemeral]
    assert len(print_questions) == len(answers)

    text = ""

    for q, a in zip(print_questions, answers):
        text += (
            '<b>"'
            + html.escape(q)
            + '"</b>: '
            + "<i>"
            + html.escape(a.label)
            + "</i>\n"
        )

    return text


@enum.unique
class KeyboardType(enum.Enum):
    """Different keyboards supported by generate keyboard"""

    INLINE_KEYBOARD = enum.auto()
    REPLY_KEYBOARD = enum.auto()
    REPLY_KEYBOARD_PERM = enum.auto()


def generate_buttons(
    buttons: Dict[str, str] | Tuple[str, str] | List[Tuple[str, str]] | List[List[str]],
    columns: int = MAX_INLINE_KEYBOARD_ROW_BUTTONS,
    header_buttons: Dict[str, str]
    | Tuple[str, str]
    | List[Tuple[str, str]]
    | List[List[str]] = None,
    footer_buttons: Dict[str, str]
    | Tuple[str, str]
    | List[Tuple[str, str]]
    | List[List[str]] = None,
    keyboard_type: KeyboardType | None = KeyboardType.INLINE_KEYBOARD,
    current_value: Optional[str] = None,
) -> Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]:
    """
    Generates Telegram Keyboard Markup from a list of buttons

    Args:
        `buttons`: Dict[str, str] | Tuple[str, str] | List[Tuple[str, str]] | List[List[str]] - list of buttons to create, except for header/footer buttons
        `columns`: int = MAX_INLINE_KEYBOARD_ROW_BUTTONS - number of buttons in one row
        `header_buttons`: Dict[str, str] | Tuple[str, str] | List[Tuple[str, str]] | List[List[str]] = None - optional buttons to be added as the first row
        `footer_buttons`: Dict[str, str] | Tuple[str, str] | List[Tuple[str, str]] | List[List[str]] = None - optional buttons to be added as the last row
        `keyboard_type`: Optional[Union[INLINE_KEYBOARD,
                                      REPLY_KEYBOARD, REPLY_KEYBOARD_PERM]] = INLINE_KEYBOARD - keyboard type to create
        `current_value`: Optional[str] = None

    Returns:
        Union[InlineKeyboardMarkup, ReplyKeyboardMarkup] - keyboard object
    """

    def check_button_list(bl) -> Dict[str, str]:
        # Check list and normalize type
        ret = {}

        match bl:
            case (str(value), str(label)):
                ret[value] = label
            case {}:
                ret = bl
            case list() as ls:
                try:
                    for button in ls:
                        ret[button[0]] = button[1]
                except IndexError:
                    raise ValueError(
                        "`buttons` must be of one of the following types: Dict[str, str] | Tuple[str, str] | List[Tuple[str, str]] | List[List[str]]"
                    )
            case _:
                raise ValueError(
                    "`buttons` must be of one of the following types: Dict[str, str] | Tuple[str, str] | List[Tuple[str, str]] | List[List[str]]"
                )

        return ret

    buttons = check_button_list(buttons)

    if len(buttons) < 1:
        raise ValueError("No values to generate buttons")

    if header_buttons is not None:
        header_buttons = check_button_list(header_buttons)

        if len(header_buttons) > MAX_INLINE_KEYBOARD_ROW_BUTTONS:
            raise ValueError(
                f"Too many header buttons. The maximum is defined by `MAX_INLINE_KEYBOARD_ROW_BUTTONS` constant and is currently: {MAX_INLINE_KEYBOARD_ROW_BUTTONS}"
            )

    if footer_buttons is not None:
        footer_buttons = check_button_list(footer_buttons)

        if len(footer_buttons) > MAX_INLINE_KEYBOARD_ROW_BUTTONS:
            raise ValueError(
                f"Too many footer buttons. The maximum is defined by `MAX_INLINE_KEYBOARD_ROW_BUTTONS` constant and is currently: {MAX_INLINE_KEYBOARD_ROW_BUTTONS}"
            )

    # define helper function to generate one button
    def generate_button(button: Dict[str, str]):
        ret = None

        value, label = next(iter(button.items()))
        if keyboard_type == KeyboardType.INLINE_KEYBOARD:
            ret = InlineKeyboardButton(text=label, callback_data=value)

            if current_value is not None and current_value == value:
                ret.text += " " + BotStrings.CURRENT_VALUE_EMOJI
        if keyboard_type in (
            KeyboardType.REPLY_KEYBOARD,
            KeyboardType.REPLY_KEYBOARD_PERM,
        ):
            ret = value

        return ret

    buttons_ordered_list = list(map(lambda it: {it: buttons[it]}, buttons))
    menu = list(
        list(map(generate_button, buttons_ordered_list[i : i + columns]))
        for i in range(0, len(buttons_ordered_list), columns)
    )

    if header_buttons:
        menu.insert(0, list(map(generate_button, header_buttons.items())))  # type: ignore
    if footer_buttons:
        menu.append(list(map(generate_button, footer_buttons.items())))  # type: ignore

    if keyboard_type == KeyboardType.INLINE_KEYBOARD:
        ret_keyboard = InlineKeyboardMarkup(menu)  # type: ignore
    else:
        ret_keyboard = ReplyKeyboardMarkup(
            menu, one_time_keyboard=keyboard_type == KeyboardType.REPLY_KEYBOARD  # type: ignore
        )

    return ret_keyboard


def log_debug(logger) -> Callable:
    def decorator(func):
        @wraps(func)
        def wrapped(*args: object, **kwargs: object):  # pylint: disable=W0613
            logger.debug("Entering: %s", func.__name__)
            result = func(*args, **kwargs)
            logger.debug("Function returned: ")
            logger.debug(result)
            logger.debug("Exiting: %s", func.__name__)
            return result

        return wrapped

    return decorator
