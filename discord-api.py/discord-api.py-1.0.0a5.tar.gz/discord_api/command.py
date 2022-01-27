from typing import Union, List

class CommandTypeUser:
    def __init__(self):
        self.number = 2

class CommandTypeMessage:
    def __init__(self):
        self.number= 3

class CommandTypeChat_Input:
    def __init__(self):
        self.number = 1

class CommandOption:
    def __init__(self, name:str, description:str = "...", type:int = 3, required:bool = False):
        self.name = name,
        self.description = description
        self.type = type,
        self.required = required

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["description"], data["type"], data.get("required"))

    def to_dict(self):
        return {
            "type": self.type[0],
            "name": self.name[0],
            "description":self.description,
            "required": self.required
        }

class Command:
    def __init__(self, name:str, description:str, options:List[CommandOption] = None, type:Union[CommandTypeUser, CommandTypeMessage, CommandTypeChat_Input] = CommandTypeChat_Input, id = None):
        self.name = name
        self.description = description
        self.type = type
        self.options = options
        if id is not None:
            self.id = id

    def to_dict(self):
        payload = {
            "type": int(self.type().number),
            "name": self.name,
            "description": self.description
        }
        if self.options is not None:
            payload["options"] = [i.to_dict() for i in self.options]
        return payload

class ApiCommand(Command):
    def __init__(self, client, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.http = client.http

    @classmethod
    def from_dict(cls, client, data):
        if data["type"] == 1:
            type = CommandTypeChat_Input().number
        elif data["type"] == 2:
            type = CommandTypeUser().number
        elif data["type"] == 3:
            type = CommandTypeMessage().number
        kwargs = {
            "name": data["name"],
            "description": data["description"],
            "type": int(type)
        }
        kwargs["id"] = data["id"]
        if data.get("options"):
            kwargs["options"] = [CommandOption.from_dict(option) for option in data["options"]]
        return cls(client, **kwargs)

    def delete(self):
        return self.http.delete_command(self.id)