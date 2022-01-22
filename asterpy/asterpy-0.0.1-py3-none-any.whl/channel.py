class Channel:
    """a channel. Shut up pylint"""
    def __init__(self, client, name):
        self.client = client
        self.name = name

    def send(self, message: str):
        self.client.send(message)
