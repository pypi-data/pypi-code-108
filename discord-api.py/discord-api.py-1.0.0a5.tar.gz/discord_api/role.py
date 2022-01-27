class Role:
    def __init__(self, data):
        self.data = data

    @property
    def id(self):
        return self.data["id"]

    @property
    def name(self):
        return self.data["name"]
        
    @classmethod
    def from_dict(cls, data):
        return cls(data)
