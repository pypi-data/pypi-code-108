class Player:
    def __init__(self, id, name, identifiers, ping):
        self.id = id
        self.name = name
        self.identifiers = Identifiers(identifiers)
        self.ping = ping

    @staticmethod
    def parse(data: dict):
        return Player(data.get('id'), data.get('name'), data.get('identifiers'), data.get('ping'))


class Identifiers:
    def __init__(self, identifiers):
        self.raw = identifiers

        self.license = None
        self.steam = None
        self.xbl = None
        self.discord = None
        self.live = None

        if identifiers is not None:
            for identifier in identifiers:
                service, id = identifier.split(':')
                if service == "license":
                    self.license = id
                elif service == "steam":
                    self.steam = id
                elif service == "xbl":
                    self.xbl = id
                elif service == "discord":
                    self.discord = id
                elif service == "live":
                    self.live = id
