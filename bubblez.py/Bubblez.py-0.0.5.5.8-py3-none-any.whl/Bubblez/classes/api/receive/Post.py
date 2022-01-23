import requests, traceback

from .Reply import Reply
from ...Color import Color
from ...Log import logTime

class Post:
    def __init__(self, client, data) -> None:
        self.client = client
        self.data = data 
        self.postid = int(data["postid"])
        self.deleted = False
        if "200" in data and data['200'] == "message sent":
            self.message = data['post']
            self.from_ = data['from']
            self.locked = data['locked']
            self.nsfw = data['pnsfw']
            self.replies = []
        else:
            self.username = data["username"]
            if "pfp" in data: self.pfp = data["pfp"]
            self.nsfw = data["pnsfw"]
            self.message = data["content"]
            self._from = data["from"]
            self.locked = data["locked"]
            self.edited = data["edited"]
            self.replies = []
            if "post_date" in data:  self.post_date = data['post_date']
            if "replies" in data and type(data['replies']) == list:
                self.replies = []
                for reply in data['replies']:
                    self.replies.append(Reply(self.client, reply))
            else: self.replies = None
    
    def edit(self, message:str):
        data, url = {"token": self.client.token, "post": message, "postid": self.postid}, self.client.live_url
        url += "/post/edit"
        response = requests.post(url=url, data=data)
        if response.ok:
            try:
                resp_js = response.json()
                if '200' in resp_js and resp_js['200'] == f'Post {self.postid} has been updated':
                    self.message = message
                    self.edited = True
                    print(f"{Color.OKGREEN}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} Post edited! {Color.ENDC}")
                    return self
                else:
                    print(f"{Color.WARNING}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} Post has not been edited! Code: {response.status_code}", Color.ENDC)
                    print(f"{Color.WARNING}Reason: {response.content}", Color.ENDC)
                    return False 
            except:
                print(f"{Color.FAIL}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} There is a error acoured on post/edit! Code: {response.status_code}", Color.ENDC)
                print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
                traceback.print_exc()
                return False
        else:      
            print(f"{Color.FAIL}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} There is a error acoured on post/edit! Code: {response.status_code}", Color.ENDC)
            print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
            traceback.print_exc()
            return False 

    def lock(self, state:bool=True):
        data, url = {"token": self.client.token, "postid": self.postid, "togglelock": str(state).lower()}, self.client.live_url
        if self.client.canary: url = self.client.canary_url
        url += "/post/lock"
        response = requests.post(url=url,data=data)
        if response.ok:
            try:
                resp_js = response.json()
                if '200' in resp_js:
                    if resp_js['200'] == f'Post {self.postid} has been locked':
                        self.locked = True
                        print(f"{Color.OKGREEN}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} Post locked! {Color.ENDC}")
                    elif resp_js['200'] == f"Post {self.postid} has been unlocked":
                        self.locked = False
                        print(f"{Color.OKGREEN}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} Post unlocked! {Color.ENDC}")
                    return self
                else:
                    print(f"{Color.WARNING}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} Post could not be locked! Code: {response.status_code}", Color.ENDC)
                    print(f"{Color.WARNING}Reason: {response.content}", Color.ENDC)
                    return False 
            except:
                print(f"{Color.FAIL}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} There is a error acoured on post/lock! Code: {response.status_code}", Color.ENDC)
                print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
                traceback.print_exc()
                return False 
        else:      
            print(f"{Color.FAIL}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} There is a error acoured on post/lock! Code: {response.status_code}", Color.ENDC)
            print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
            traceback.print_exc()
            return False 

    def unlock(self): self.lock(False)

    def delete(self):
        url, data = self.client.live_url, {"token": self.client.token, "postid": self.postid, "confirm": "true"}
        if self.client.canary: url = self.client.canary_url
        url += "/post/delete"
        response = requests.post(url=url, data=data)
        if response.ok:
            try:
                resp_js = response.json()
                if '200' in resp_js:
                    if resp_js['200'] == f'Post {self.postid} has been deleted':
                        self.deleted = True
                        print(f"{Color.OKGREEN}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} Post deleted! {Color.ENDC}")
                        return True 
                else:
                    print(f"{Color.WARNING}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} Post has not been deleted! Code: {response.status_code}", Color.ENDC)
                    print(f"{Color.WARNING}Reason: {response.content}", Color.ENDC)
                    return False 
            except:
                print(f"{Color.FAIL}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} There is a error acoured on post/delete! Code: {response.status_code}", Color.ENDC)
                print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
                traceback.print_exc()
                return False 
        else:      
            print(f"{Color.FAIL}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} There is a error acoured on post/delete! Code: {response.status_code}", Color.ENDC)
            print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
            traceback.print_exc()
            return False 

    def reply(self, message:str, from_:str=None, nsfw:bool=False):

        data, url = {"token": self.client.token, "reply": message, "from": from_, "nsfw": str(nsfw).lower(), "postid": self.postid}, self.client.live_url
        if self.client.canary: url = self.client.canary_url
        url += "/reply/send"
        response = requests.post(url=url, data=data)
        if response.ok:
            try:
                resp_js = response.json()
                if '200' in resp_js:
                    if resp_js['200'] == f'reply sent':
                        self.replies.append(Reply(self.client, resp_js))
                        print(f"{Color.OKGREEN}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} Reply send! {Color.ENDC}")
                        return self 
                else:
                    print(f"{Color.WARNING}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} Post has not been send! Code: {response.status_code}", Color.ENDC)
                    print(f"{Color.WARNING}Reason: {response.content}", Color.ENDC)
                    return False 
            except:
                print(f"{Color.FAIL}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} There is a error acoured on post/reply! Code: {response.status_code}", Color.ENDC)
                print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
                traceback.print_exc()
                return False 
        else:      
            print(f"{Color.FAIL}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} There is a error acoured on post/reply! Code: {response.status_code}", Color.ENDC)
            print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
            traceback.print_exc()
            return False 
        
    def get_all_replies(self):
        return self.replies
    
    def json(self):
        return self.data
    