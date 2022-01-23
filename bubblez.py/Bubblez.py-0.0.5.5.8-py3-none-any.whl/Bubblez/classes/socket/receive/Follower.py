from ...Color import Color
from ...Log import logTime


class Follower:
    def __init__(self, follower_id, user_data) -> None:
        self.follower_id = follower_id
        self.user_data = user_data
        
        self.username = user_data['username']
        self.uuid = user_data['uuid']

    def json(self):
        return {
            "follower_id": self.follower_id,
            "user": self.user_data
        }