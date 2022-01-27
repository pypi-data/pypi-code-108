from .user import User
from .channel import Channel

class Message:
    """Represents a message in a channel on the server"""
    def __init__(self, content: str, user: User, channel: Channel, date: int):
        self.content = content
        self.author = user
        self.channel = channel
        self.date = date

    def to_json(self):
        """Convert the Message object to JSON"""
        return {"content": self.content, "author_uuid": self.author.uuid, "date": self.date}
    
