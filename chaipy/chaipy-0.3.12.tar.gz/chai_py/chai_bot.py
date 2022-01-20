from typing import List
import logging
import sys

from typing_extensions import final

from chai_py.logger import ColoredFormatter
from chai_py.types import Update, Message


class ChaiBot:
    """Base chatbot class.

    Chatbots must be made as a subclass of ChaiBot.
    The subclass must then implement the on_message() method, with the same signature.
    """
    # When starting a conversation with the bot, the app first sends a message with this string.
    # By detecting and responding to this string, the bot can conveniently provide a custom conversation opener.
    # This attribute is only for convenience; overriding this string does not change the string the bot will receive.
    FIRST_MESSAGE_STRING = "__first"

    @final
    def __init__(self, uid: str = "LOCAL_DEV"):
        self._bot_uid = uid
        self.logger = logging.getLogger(self.__class__.__name__)
        self.setup_logger()

        self.setup()

    async def on_message(self, update: Update) -> str:
        """Event called when the bot receives a message.

        @param update:
        @return:
            String containing the reply.
        """
        raise NotImplementedError

    async def get_messages(self, conversation_id: str) -> List[Message]:
        """Fetches a list of messages for the specified conversation.

        This function is provided when using bots in a :class:TRoom and in deployment.
        Do not override or create an implementation.

        @param conversation_id:
        @return:
            List of messages in the conversation, sorted by increasing timestamp (i.e. oldest first).
        """
        raise NotImplemented

    def setup_logger(self):
        formatter = ColoredFormatter.default_chai_formatter()
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        self.logger.handlers = []
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def setup(self):
        """Any setup should be done by overriding this function."""
        pass
