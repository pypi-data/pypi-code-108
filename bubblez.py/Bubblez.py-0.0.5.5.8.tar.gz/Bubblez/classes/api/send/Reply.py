from ...Color import Color
from ...Log import logTime

from ..receive.Reply import Reply as ReceiveReply
import requests, traceback

class Reply:
    def __init__(self, client) -> None:
        self.client = client

    def send(self, message:str, postid:int, from_:str=None, nsfw:bool=False):
        """
        Sending a Reply!
            message: `str` The message in a Reply!
            from_: `str` The little message next to the date send!
            nsfw: `bool` If set, User without Date of Birth or nsfw set cannot see it!
        """
        data, url = {"token": self.client.token, "reply": message, "from": from_, "nsfw": str(nsfw).lower(), "postid": postid}, self.client.live_url
        if self.client.canary: url = self.client.canary_url
        url += "/reply/send"
        response = requests.post(url=url, data=data)
        if response.ok:
            try:
                resp_js = response.json()
                if '200' in resp_js:
                    if resp_js['200'] == f'reply sent':
                        print(f"{Color.OKGREEN}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} Reply send! {Color.ENDC}")
                        return ReceiveReply(self.client, resp_js)
                else:
                    print(f"{Color.WARNING}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} reply has not been send! Code: {response.status_code}", Color.ENDC)
                    print(f"{Color.WARNING}Reason: {response.content}", Color.ENDC)
                    return 
            except:
                print(f"{Color.FAIL}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} There is a error acoured on reply/send! Code: {response.status_code}", Color.ENDC)
                print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
                traceback.print_exc()
                return False 
        else:      
            print(f"{Color.FAIL}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} There is a error acoured on reply/send! Code: {response.status_code}", Color.ENDC)
            print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
            traceback.print_exc()
            return False 

    def delete(self, replyid:int):
        """
        Delete a Reply!
            replyid: `int` The reply id
        """
        url, data = self.client.live_url, {"token": self.client.token, "replyid": replyid, "confirm": "true"}
        if self.client.canary: url = self.client.canary_url
        url += "/reply/delete"
        response = requests.post(url=url, data=data)
        if response.ok:
            try:
                resp_js = response.json()
                if '200' in resp_js:
                    if resp_js['200'] == f'reply {replyid} has been deleted':
                        print(f"{Color.OKGREEN}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} Reply deleted! {Color.ENDC}")
                        return True
                else:
                    print(f"{Color.WARNING}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} reply has not been deleted! Code: {response.status_code}", Color.ENDC)
                    print(f"{Color.WARNING}Reason: {response.content}", Color.ENDC)
                    return False
                
            except:
                print(f"{Color.FAIL}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} There is a error acoured on reply/delete! Code: {response.status_code}", Color.ENDC)
                print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
                traceback.print_exc()
                return False 
        else:      
            print(f"{Color.FAIL}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} There is a error acoured on reply/delete! Code: {response.status_code}", Color.ENDC)
            print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
            traceback.print_exc()
            return False

    def edit(self, message:str, replyid:int):
        """
        edit a Reply!
            replyid: `int` The reply id
            message: `str` The messge in the reply
        """
        data, url = {"token": self.client.token, "reply": message, "replyid": replyid}, self.client.live_url
        url += "/reply/edit"
        response = requests.post(url=url, data=data)
        if response.ok:
            try:
                resp_js = response.json()
                if '200' in resp_js and resp_js['200'] == f'Reply {replyid} has been updated':
                    print(f"{Color.OKGREEN}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} Reply edited! {Color.ENDC}")
                    return True
                else:
                    print(f"{Color.WARNING}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} reply has not been edited! Code: {response.status_code}", Color.ENDC)
                    print(f"{Color.WARNING}Reason: {response.content}", Color.ENDC)
                    return False 
            except:
                print(f"{Color.FAIL}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} There is a error acoured on reply/edit! Code: {response.status_code}", Color.ENDC)
                print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
                traceback.print_exc()
                return False
        else:      
            print(f"{Color.FAIL}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} There is a error acoured on reply/edit! Code: {response.status_code}", Color.ENDC)
            print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
            traceback.print_exc()
            return False 