from .user import User
from .channel import Channel

class Message:
    """Represents a message in a channel on the server"""
    def __init__(self, content: str, user: User, channel: Channel):
        self.content = content
        self.user = user
        self.channel = channel
