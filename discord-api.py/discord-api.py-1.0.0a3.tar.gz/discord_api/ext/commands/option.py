class Option:
    def __init__(self, description:str = "...", type:int = 3):
        self.description = description
        self.type = type

    def to_dict(self):
        return {
            "type": type,
            "description":self.description,
            "required": self.required
        }
