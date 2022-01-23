
from ...Color import Color
from ...Log import logTime

from .Post import Post
from .Reply import Reply

import json, traceback, requests

class User:
    def __init__(self, client, data) -> None:
        self.client = client
        self.raw_json = data 
        if "dob" in data: self.dob = data['dob']
            
        self.uuid = data['uuid']
        self.username = data['username']
        self.display_name = data['displayname']
        if "followers" in data: self.followers = data["followers"]
        self.pfp = data["pfp"]
        self.banner = data["banner"]
        self.coins = data["coins"]
        self.rank = data["rank"]
        self.eventr = data["eventr"]
        self.patreon = data["patreon"][0].upper()
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
                print(f"{Color.OKCYAN}[Bubblez.py-websockets-{self.client.prefix_log}] {logTime()} There where no posts found when fetching user! {Color.ENDC}")

        if "replies" in data and type(data['replies']) == list:
            self.replies = []
            for reply in data['replies']:
                self.replies.append(Reply(self.client, reply))
        else:
            self.replies = None 
            if self.client.verbose:
                print(f"{Color.OKCYAN}[Bubblez.py-websockets-{self.client.prefix_log}] {logTime()} There where no replies found when fetching user! {Color.ENDC}")


    def update(self):
        """
        Updating the user class!
        """
        data, url = {"token": self.client.token, "username": self.username}, self.client.live_url 
        if self.client.canary: url = self.client.canary_url
        url += "/user/get"
        response = requests.post(url=url, data=data)
        if response.ok:
            try:
                resp_js = response.json()
                if '200' in resp_js and resp_js['200'] == f'Found user':
                    print(f"{Color.OKGREEN}[Bubblez.py-websockets-{self.client.prefix_log}] {logTime()} User ({resp_js['username']}) Found, updating the class! {Color.ENDC}")
                    return User(self.client, resp_js)
                else:
                    print(f"{Color.WARNING}[Bubblez.py-websockets-{self.client.prefix_log}] {logTime()} User has not been found! Code: {response.status_code}", Color.ENDC)
                    print(f"{Color.WARNING}Reason: {response.content}", Color.ENDC)
                    return False 
            except:
                print(f"{Color.FAIL}[Bubblez.py-websockets-{self.client.prefix_log}] {logTime()} There is a error acoured on user/get! Code: {response.status_code}", Color.ENDC)
                print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
                traceback.print_exc()
                return False
        else:
            print(f"{Color.FAIL}[Bubblez.py-websockets-{self.client.prefix_log}] {logTime()} There is a error acoured on user/get! Code: {response.status_code}", Color.ENDC)
            print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
            traceback.print_exc()
            return False

    def get_all_replies(self):
        return self.replies

    def get_all_posts(self):
        return self.posts

    def json(self):
        return self.raw_json

