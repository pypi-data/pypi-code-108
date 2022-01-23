import requests, traceback

from .Reply import Reply
from ...Color import Color
from ...Log import logTime

class Post:
    def __init__(self, client, data) -> None:
        self.client = client
        self.raw_data = data
        self.postid = int(data["postid"])
        self.deleted = False 
        self.message = None 
        self.username = data['username']

        if "post" in data: self.message = data['post']
        if "content" in data: self.message = data['content']
        if "editedcontent" in data: self.message = data['editedcontent']
        self.from_ = data['from']
        self.locked = data['locked']
        self.pnsfw = data['pnsfw']

        if "edited" in data: self.edited_on = data["edited"]
        if "post_date" in data: self.posted_on = data['post_date']
    
        if "replies" in data and type(data['replies']) == list:
            self.replies = []
            for reply in data['replies']:
                self.replies.append(Reply(self.client, reply))
        else: self.replies = None

    def edit(self, message:str):
        """
        Editing the post thro the Bubblez api!
        
        message : `str`
        """
        data, url = {"token": self.client.token, "post": message, "postid": self.postid}, self.client.live_url
        url += "/post/edit"
        response = requests.post(url=url, data=data)
        if response.ok:
            try:
                resp_js = response.json()
                if '200' in resp_js and resp_js['200'] == f'Post {self.postid} has been updated':
                    self.message = message
                    self.edited = True
                    print(f"{Color.OKGREEN}[Bubblez.py-websockets-{self.client.prefix_log}] {logTime()} Post edited! {Color.ENDC}")
                    return self
                else:
                    print(f"{Color.WARNING}[Bubblez.py-websockets-{self.client.prefix_log}] {logTime()} Post has not been edited! Code: {response.status_code}", Color.ENDC)
                    print(f"{Color.WARNING}Reason: {response.content}", Color.ENDC)
            except:
                print(f"{Color.FAIL}[Bubblez.py-websockets-{self.client.prefix_log}] {logTime()} There is a error acoured on post/edit! Code: {response.status_code}", Color.ENDC)
                print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
                traceback.print_exc()
                return False
        else:      
            print(f"{Color.FAIL}[Bubblez.py-websockets-{self.client.prefix_log}] {logTime()} There is a error acoured on post/edit! Code: {response.status_code}", Color.ENDC)
            print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
            traceback.print_exc()
            return False 

    def lock(self, state:bool=True):
        """
        Locking the post thro the Bubblez api!
        
        locked : `bool`\n
        if the post is locked, no-one can reply to it!
        """
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
                        print(f"{Color.OKGREEN}[Bubblez.py-websockets-{self.client.prefix_log}] {logTime()} Post locked! {Color.ENDC}")
                    elif resp_js['200'] == f"Post {self.postid} has been unlocked":
                        self.locked = False
                        print(f"{Color.OKGREEN}[Bubblez.py-websockets-{self.client.prefix_log}] {logTime()} Post unlocked! {Color.ENDC}")
                    return self
            except:
                print(f"{Color.FAIL}[Bubblez.py-websockets-{self.client.prefix_log}] {logTime()} There is a error acoured on post/lock! Code: {response.status_code}", Color.ENDC)
                print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
                traceback.print_exc()
                return False 
        else:      
            print(f"{Color.FAIL}[Bubblez.py-websockets-{self.client.prefix_log}] {logTime()} There is a error acoured on post/lock! Code: {response.status_code}", Color.ENDC)
            print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
            traceback.print_exc()
            return False 

    def unlock(self):
        """
        Unlocking the post thro the Bubblez api!
        """
        self.lock(False)

    def delete(self):        
        """
        Deleting the post thro the Bubblez api!
        """
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
                        print(f"{Color.OKGREEN}[Bubblez.py-websockets-{self.client.prefix_log}] {logTime()} Post deleted! {Color.ENDC}")
                        return True 
            except:
                print(f"{Color.FAIL}[Bubblez.py-websockets-{self.client.prefix_log}] {logTime()} There is a error acoured on post/delete! Code: {response.status_code}", Color.ENDC)
                print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
                traceback.print_exc()
                return False 
        else:      
            print(f"{Color.FAIL}[Bubblez.py-websockets-{self.client.prefix_log}] {logTime()} There is a error acoured on post/delete! Code: {response.status_code}", Color.ENDC)
            print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
            traceback.print_exc()
            return False 

    def reply(self, message:str, from_:str=None, nsfw:bool=False):
        """
        Replying to the post!

        message: `str` 
        from_: `str` This is a little message in the post, You can see it next to the date of the post!
        nsfw: `bool` If True, than u need to have nsfw enabled and Date Of Birth set in your settings, otherwise you can not see it!
        """
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
                        print(f"{Color.OKGREEN}[Bubblez.py-websockets-{self.client.prefix_log}] {logTime()} Reply send! {Color.ENDC}")
                        return self 
                else:
                    print(f"{Color.WARNING}[Bubblez.py-websockets-{self.client.prefix_log}] {logTime()} Reply has not been send! Code: {response.status_code}", Color.ENDC)
                    print(f"{Color.WARNING}Reason: {response.content}", Color.ENDC)
                    return False 
            except:
                print(f"{Color.FAIL}[Bubblez.py-websockets-{self.client.prefix_log}] {logTime()} There is a error acoured on post/reply! Code: {response.status_code}", Color.ENDC)
                print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
                traceback.print_exc()
                return False 
        else:      
            print(f"{Color.FAIL}[Bubblez.py-websockets-{self.client.prefix_log}] {logTime()} There is a error acoured on post/reply! Code: {response.status_code}", Color.ENDC)
            print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
            traceback.print_exc()
            return False 
        
    def get_all_replies(self):
        return self.replies
    
    def json(self):
        return self.raw_data