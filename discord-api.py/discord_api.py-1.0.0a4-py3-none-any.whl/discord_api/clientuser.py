class ClientUser:
    """
    Attributes
    ----------
    id : str
        return a bot's id.
    name : str
        return a bot's name.
    discriminator : str
        return a bot's discriminator.
    """
    def __init__(self, data):
        self.id = data["id"]
        self.name = data["username"]
        self.avatar = data["avatar"]
        self.discriminator = data["discriminator"]
        
    @classmethod
    def from_dict(cls, data):
        return cls(data)
