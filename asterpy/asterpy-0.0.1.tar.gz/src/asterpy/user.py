class User:
    """Represents a user on the aster server"""
    def __init__(self, uuid: int, username: str):
        self.uuid = uuid
        self.username = username
