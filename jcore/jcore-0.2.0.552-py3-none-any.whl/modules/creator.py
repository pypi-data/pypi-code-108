from datetime import datetime
from jcore.extensions import Module
from jcore.message import Join
import jcore

class Creator(Module):
    def __init__(self, client: jcore.Client, name: str):
        Module.__init__(self, name)
        self.client = client
        self.launchTime = datetime.now()


    async def on_join(self, message: Join):
        if "cubbei" == message.user and (datetime.now() - self.launchTime).seconds > 60:
            await message.send_action("bows to the creator")
            



def setup(client: jcore.Client):
    client.load_module(Creator(client, "Creator"))

