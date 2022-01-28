from jcore.extensions import Module
from jcore.message import PrivateMessage, CommandMessage
import jcore

class Ping(Module):
    def __init__(self, client: jcore.Client, name: str):
        Module.__init__(self, name)
        self.client = client


    async def on_privmessage(self, message: PrivateMessage):
        if message.user_id == "82504138":
            if "ping" == message.message_text:
                await message.send("pong...")
            elif "peanut" == message.message_text:
                await message.send("butter! Kappa")

    async def on_command(self, message: CommandMessage):
        if message.user_id == "82504138":
            if "ping" == message.KEYWORD:
                await message.send("pong...")
            elif "peanut" == message.KEYWORD:
                await message.send("butter! Kappa")
                


def setup(client: jcore.Client):
    client.load_module(Ping(client, "Ping"))

