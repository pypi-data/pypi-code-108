from ...Color import Color
from ...Log import logTime


class Devlog:
    def __init__(self, client, data) -> None:
        self.client = client
        self.raw_json = data 

        self.blogid = int(data['blogid'])
        self.blogposter_username = data['blogposter_username']
        self.blogposter_displayname = data['blogposter_displayname']
        self.blogposter_pfp = data['blogposter_pfp']
        self.blogcontent = data["blogcontent"]
        self.blogdate = data['blogdate']
    
    def json(self):
        return self.raw_json
