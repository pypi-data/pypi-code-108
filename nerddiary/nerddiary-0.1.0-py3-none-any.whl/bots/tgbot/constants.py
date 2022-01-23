""" This module contains all bot constants """
import enum


# ------------ Handler groups ------------
@enum.unique
class HandlerGroup(enum.IntEnum):
    """Handler groups - processed in the order SPAM_CONTROL -> ADMIN -> BASE -> CONVERSATION"""

    SPAM_CONTROL = -1
    """ Handler group where the basic spam control goes into, must be smaller than any other group to be processed first """
    ADMIN = 0
    """ Handler group where all admin handlers go, must be smaller than any other group to be processed first """
    BASE = 1
    """ Handler group where all messages (inside or outside of a converstaion) go, must be smaller than groups for conversation handlers """
    COONVERSATION = 2
    """ Handler group where all admin handlers go, must be smaller than any other group to be processed first """


# ------------ Bot conversation state defs ------------
@enum.unique
class PollState(enum.IntEnum):
    """State definitions for new row entry"""

    CONFIRMING_ROW = enum.auto()
    CHOOSING_SELECT_VALUE = enum.auto()


# ------------ Bot context dicts (user_data, chat_data, bot_data) keys ------------
@enum.unique
class ContextKey(enum.Enum):
    """Various keys used in context dicts"""

    CHAT_CONTEXT = enum.auto()
    """ Key for ChatContext object """
    BOT_ADMIN = enum.auto()
    """ Current instance of BotAdmin """
    BOT_ADMIN_USER_ACTION = enum.auto()
    """ Used in BotAdmin - id of the user whose join request is being processed """
    BOT_CONFIG = enum.auto()
    """ Current instance of BotConfig """
    BOT_USERS = enum.auto()
    """ List of loaded user configs """


# ------------ Keyboard generation related constants ------------
MAX_INLINE_KEYBOARD_ROW_BUTTONS = 4


# ------------ Special buttons ------------
@enum.unique
class KeyboardAdminModerate(tuple, enum.Enum):
    """Special button group for admin moderation actions"""

    BUTTON_ADMIN_ALLOW = ("allow", "Allow")
    """ Special value used to allow user """
    BUTTON_ADMIN_BAN = ("ban", "Ban")
    """ Special value used to ban user """
    BUTTON_ADMIN_DONOTHING = ("later", "Decide later")


@enum.unique
class KeyboardRowSaveCancel(tuple, enum.Enum):
    """Special buttons group to confirm row save"""

    BUTTON_CONFIRM_ROW = ("ok", "Все правильно👌")
    BUTTON_CANCEL_ROW = ("oops", "Упс, нужно поправить🔧")
