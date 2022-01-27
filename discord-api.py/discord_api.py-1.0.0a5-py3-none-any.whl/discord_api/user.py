class User:
    def __init__(self, client, data):
        self.name = data["username"]
        self.id = data["id"]
        self.discriminator = data["discriminator"]
        self.avatar = data["avatar"]

    @classmethod
    def from_dict(cls, client, data):
        return cls(client, data)