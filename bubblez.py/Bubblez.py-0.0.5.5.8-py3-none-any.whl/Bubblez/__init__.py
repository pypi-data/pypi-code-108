
"""
This is a Bubblez Lib for the https://bubblez.app api and the websockets!
"""

from .classes.api.send.User import User
from .classes.api.send.Devlog import Devlog
from .classes.api.send.Post import Post
from .classes.api.send.Reply import Reply
from .classes.api.Setup import Setup


class Bubblez:
    live_url = "https://bubblez.app/api/v1"
    canary_url = "https://canary.bubblez.app/api/v1"

    def __init__(self, token, verbose=False, use_canary=False) -> None:
        self.token = token 
        self.authenticated = False 
        self.verbose = verbose
        self.canary = use_canary
        if self.canary: self.prefix_log = "canary"
        else: self.prefix_log = "live"

        _user = Setup(self).login()
        if _user == None: return 
        self.username  = _user['username']
        self.displayname = _user['displayname']
    
        self.user = User(self)
        self.devlog = Devlog(self)
        self.post = Post(self)
        self.reply = Reply(self)
