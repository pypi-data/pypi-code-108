from ...Color import Color
from ...Log import logTime
from .Post import Post
from .Reply import Reply
from .User import User

class Edit:
    def __init__(self, client, type, incomming) -> None:
        self.client = client
        self.raw_json = incomming 

        self.post = None 
        if str(type).lower() == "post":
            self.post = Post(client, incomming['postdata'])
        
        self.reply = None 
        if str(type).lower() == "reply":
            self.reply = Reply(client, incomming['replydata'])

        self.user = User(client, incomming['userdata'])


    def json(self):
        return self.raw_json

