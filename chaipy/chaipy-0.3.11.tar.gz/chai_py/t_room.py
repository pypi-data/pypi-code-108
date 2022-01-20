from typing import Sequence
import asyncio
import time
import uuid

from chai_py.chai_bot import ChaiBot
from chai_py.types import Update, LatestMessage, Message, MessageKind


class TRoom():
    """Code for testing your bot locally. """

    def __init__(self, bots: Sequence[ChaiBot]):
        self.bots = bots
        self.conversation_id = str(uuid.uuid4())
        self.messages = []
        if len(self.bots) == 0:
            raise RuntimeError("Cannot start with no bots.")
        print("Starting TRoom. Press ctrl-c to escape.")
        self.setup_bots()

    def chat(self):
        asyncio.run(self._loop())

    def test_chat(self, messages):
        asyncio.run(self._message_loop(messages))

    async def _message_loop(self, messages):
        await self.send_message(self.bots[0].FIRST_MESSAGE_STRING)

        for message in messages:
            await self.send_message(message)

    async def _loop(self):
        await self.send_message(self.bots[0].FIRST_MESSAGE_STRING)
        while True:
            try:
                message = input("Enter your message: ")
            except KeyboardInterrupt:
                print("Interrupted TRoom.")
                break
            await self.send_message(message)

    def setup_bots(self):
        async def get_messages_local(conversation_id: str):
            return self.messages

        for bot in self.bots:
            bot.get_messages = get_messages_local

    async def send_message(self, message: str):
        timestamp = int(time.time() * 1000)
        print(f"<<< {message}")
        self.messages.append(
            Message(
                sender_uid='__local_dev',
                timestamp=timestamp,
                message_kind=MessageKind.TEXT,
                content=message,
            )
        )
        update = Update(
            conversation_id=self.conversation_id,
            latest_message=LatestMessage(
                text=message,
                timestamp=timestamp
            )
        )

        for coro in asyncio.as_completed([self._bot_on_message(bot, update) for bot in self.bots]):
            bot, result = await coro
            print(f">>> {result}")
            self.messages.append(
                Message(
                    sender_uid=bot._bot_uid,
                    timestamp=timestamp,
                    message_kind=MessageKind.TEXT,
                    content=result,
                )
            )

    @staticmethod
    async def _bot_on_message(bot: ChaiBot, update: Update):
        result = await bot.on_message(update)
        return bot, result


TestRoom = TRoom
