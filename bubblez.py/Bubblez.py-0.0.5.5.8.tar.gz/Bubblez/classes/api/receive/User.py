
from ...Color import Color
from ...Log import logTime

from .Post import Post
from .Reply import Reply

import json, traceback

class User:
    def __init__(self, client, data) -> None:
        self.client = client
        self.raw_json = data 
        self.uuid = data['uuid']
        self.username = data['username']
        self.display_name = data['displayname']
        if "dob" in data: self.dob = data['dob']
        if "followers" in data: self.followers = data["followers"]
        self.pfp = data["pfp"]
        self.banner = data["banner"]
        self.coins = data["coins"]
        self.rank = data["rank"]
        self.eventr = data["eventr"]
        self.patreon = data["patreon"][0]
        self.booster = data["booster"]
        self.bio = data["bio"]
        self.nsfw = data["nsfw"]
        self.pronoun = data["pronoun"]
        self.created_at = data["created_at"]
        self.last_posted = data['last_posted']
        self.ban = data['ban']
        if "posts" in data and type(data['posts']) == list:
            self.posts = []
            for post in data["posts"]:
                self.posts.append(Post(self.client, post))
        else:
            self.posts = None 
            if self.client.verbose:
                print(f"{Color.WARNING}[Bubblez.py-{self.client.prefix_log}] {logTime()} There where no posts found! {Color.ENDC}")

        if "replies" in data and type(data['replies']) == list:
            self.replies = []
            for reply in data['replies']:
                self.replies.append(Reply(self.client, reply))
        else:
            self.replies = None 
            if self.client.verbose:
                print(f"{Color.OKCYAN}[Bubblez.py-{self.client.prefix_log}] {logTime()} There where no replies found! {Color.ENDC}")

    def json(self):
        return self.raw_json

