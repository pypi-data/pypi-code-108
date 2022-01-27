class Channel:
    """a channel. Shut up pylint"""
    def __init__(self, client, name, uuid):
        self.client = client
        self.name = name
        self.uuid = uuid

    def send(self, message: str):
        rejoin_channel = None
        if self.client.current_channel != self:
            rejoin_channel = self.client.current_channel
            self.client.join(self)
        
        self.client.send(message)
        if rejoin_channel is not None:
            self.client.join(rejoin_channel)
