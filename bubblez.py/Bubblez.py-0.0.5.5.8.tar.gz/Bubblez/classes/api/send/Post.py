
from ...Color import Color
from ...Log import logTime
from ..receive.Post import Post as ReceivedPost

import requests, traceback

class Post:
    def __init__(self, client) -> None:
        self.client = client

    def send(self, message:str, from_:str=None, locked:bool=False, nsfw:bool=False):
        """
        Sending a Post!
            message: `str` The messag in a post!
            from_: `str` The little message next to the date send!
            locked: `bool` If True, no-one can reply than!
            nsfw: `bool` If set, User without Date of Birth or nsfw set cannot see it!
        """
        url, data = self.client.live_url, {"post": message} 
        if self.client.canary:
            url = self.client.canary_url 
        url += '/post/send'
        if from_: data['from'] = from_
        if locked: data['locked'] = str(locked).lower()
        if nsfw: data['nsfw'] = str(nsfw).lower()
        if self.client.token: data['token'] = self.client.token
        if not message:
            print(f"[Bubblez.py-api-{self.client.prefix_log}] {logTime()} Please provide a message to post!")
            return False 

        response = requests.post(url=url, data=data)
        if response.ok:
            try:
                resp_js = response.json()
                if '200' in resp_js and resp_js['200'] == 'message sent':
                    print(f"{Color.OKGREEN}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} Post send! {Color.ENDC}")
                    return ReceivedPost(self.client, resp_js)
                else:
                    print(f"{Color.FAIL}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} Did not send post! Code: {response.status_code}", Color.ENDC)
                    print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
                    return False 
            except:
                print(f"{Color.FAIL}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} There is a error acoured on post/send! Code: {response.status_code}", Color.ENDC)
                print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
                return False 
        else:      
            print(f"{Color.FAIL}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} There is a error acoured on post/send! Code: {response.status_code}", Color.ENDC)
            print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
        return False 

    def get(self, postid:int):
        """
        Get a Post!
            postid: `int` The post id!
        """
        data, url = {"token": self.client.token, "postid": postid}, self.client.live_url
        if self.client.canary: url = self.client.canary_url
        url += "/post/get"
        response = requests.post(url=url, data=data)
        if response.ok:
            try:
                resp_js = response.json()
                if '200' in resp_js and resp_js['200'] == "Found post":
                    print(f"{Color.OKGREEN}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} Post found!", Color.ENDC)
                    return ReceivedPost(self.client, resp_js)
                elif resp_js['posts'] == None:
                    print(f"{Color.WARNING}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} No post found with id: {postid}!", Color.ENDC)
                    return False 
            except:
                print(f"{Color.FAIL}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} There is a error acoured on post/get!", Color.ENDC)
                print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
                return False
        else:
            print(f"{Color.FAIL}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} There is a error acoured on post/get!", Color.ENDC)
            print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
        return False
    
    def lock(self, postid:int, togglelock:bool=True):
        """
        Lock or unlock a Post!
            postid: `int` The post id
            togglelock: `bool` True, than no-one can reply
        """
        data, url = {"token": self.client.token, "postid": postid, "togglelock": str(togglelock).lower()}, self.client.live_url
        if self.client.canary: url = self.client.canary_url
        url += "/post/lock"
        response = requests.post(url=url,data=data)
        if response.ok:
            try:
                resp_js = response.json()
                if '200' in resp_js:
                    if resp_js['200'] == f'Post {postid} has been locked':
                        print(f"{Color.OKGREEN}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} Post locked! {Color.ENDC}")
                    elif resp_js['200'] == f"Post {postid} has been unlocked":
                        print(f"{Color.OKGREEN}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} Post unlocked! {Color.ENDC}")
                    return True 
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
    
    def unlock(self, postid:int):
        self.lock(postid, False)
    
    def delete(self, postid:int):
        """
        Delete a Post!
            postid: `int` A post id!
        """
        url, data = self.client.live_url, {"token": self.client.token, "postid": postid, "confirm": "true"}
        if self.client.canary: url = self.client.canary_url
        url += "/post/delete"
        response = requests.post(url=url, data=data)
        if response.ok:
            try:
                resp_js = response.json()
                if '200' in resp_js:
                    if resp_js['200'] == f'Post {postid} has been deleted':
                        print(f"{Color.OKGREEN}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} Post deleted! {Color.ENDC}")
                        return True 
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

    def get_latest(self, id_only:bool=False):
        """
        Get the latest post!
            id_only: `bool` If True, it will only return the post_id, else it will return a Post Object 
        """
        data, url = {"token": self.client.token}, self.client.live_url
        if self.client.canary: url = self.client.canary_url
        url += "/post/latest"
        response = requests.post(url=url, data=data)
        if response.ok:
            try:
                resp_js = response.json()
                if '200' in resp_js and resp_js['200'] == "latest Post":
                    print(f"{Color.OKGREEN}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} Latest post id found!", Color.ENDC)
                    if id_only: return resp_js['postid']
                    else: return self.get(resp_js['postid'])
            except:
                print(f"{Color.FAIL}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} There is a error acoured on post/latest!", Color.ENDC)
                print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
                return False
        else:
            print(f"{Color.FAIL}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} There is a error acoured on post/latest!", Color.ENDC)
            print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
        return False