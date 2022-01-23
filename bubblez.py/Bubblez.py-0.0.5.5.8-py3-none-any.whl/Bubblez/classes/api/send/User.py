from ...Color import Color
from ...Log import logTime

from ..receive.User import User as ReceivedUser
from ..receive.Post import Post as ReceivedPost
from ..receive.Reply import Reply as ReceivedReply

import requests, traceback, json

class User:
    def __init__(self, client) -> None:
        self.client = client

    def get(self, username:str):
        """
        Get a user with username!
            username: `str`
        """
        data, url = {"token": self.client.token, "username": username}, self.client.live_url 
        if self.client.canary: url = self.client.canary_url
        url += "/user/get"
        if self.client.verbose: 
            print(Color.OKCYAN, f"[Bubblez.py-api-{self.client.prefix_log}]Sending API request to: {Color.BOLD}/user/get", Color.ENDC)
        response = requests.post(url=url, data=data)
        if response.ok:
            try:
                resp_js = response.json()
                if '200' in resp_js and resp_js['200'] == f'Found user':
                    print(f"{Color.OKGREEN}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} Api found user: {resp_js['username']} {Color.ENDC}")
                    return ReceivedUser(self.client, resp_js)
                else:
                    print(f"{Color.WARNING}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} Did not find user! Code: {response.status_code}", Color.ENDC)
                    print(f"{Color.WARNING}Reason: {response.content}", Color.ENDC)
                    return False 
            except:
                print(f"{Color.FAIL}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} There is a error acoured on user/get! Code: {response.status_code}", Color.ENDC)
                print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
                traceback.print_exc()
                return False
        else:
            print(f"{Color.FAIL}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} There is a error acoured on user/get! Code: {response.status_code}", Color.ENDC)
            print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
            traceback.print_exc()
            return False

    def check(self):
        """
        Check your token!
        """
        data, url = {"token": self.client.token}, self.client.live_url 
        if self.client.canary: url = self.client.canary_url
        url += "/user/check"
        response = requests.post(url=url, data=data)
        if response.ok:
            try:
                resp_js = response.json()
                if '200' in resp_js and resp_js['200'] == f'Found user':
                    print(f"{Color.OKGREEN}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} User found with username: {resp_js['username']}! {Color.ENDC}")
                    return ReceivedUser(self.client, resp_js)
                else:
                    print(f"{Color.WARNING}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} Could not find user! Code: {response.status_code}", Color.ENDC)
                    print(f"{Color.WARNING}Reason: {response.content}", Color.ENDC)
                    return False 
            except:
                print(f"{Color.FAIL}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} There is a error acoured on user/check! Code: {response.status_code}", Color.ENDC)
                print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
                traceback.print_exc()
                return False
        else:
            print(f"{Color.FAIL}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} There is a error acoured on user/check! Code: {response.status_code}", Color.ENDC)
            print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
            traceback.print_exc()
            return False 
    
    def ping(self):
        """
        Set your status to online!
        """
        data, url = {"token": self.client.token}, self.client.live_url 
        if self.client.canary: url = self.client.canary_url
        url += "/user/check"
        response = requests.post(url=url, data=data)
        if response.ok:
            try:
                resp_js = response.json()
                if '200' in resp_js and resp_js['200'] == f'Pong':
                    print(f"{Color.OKGREEN}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} User found with username: {resp_js['username']}! {Color.ENDC}")
                    return True 
                else:
                    print(f"{Color.WARNING}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} Could not find user with token! Code: {response.status_code}", Color.ENDC)
                    print(f"{Color.WARNING}Reason: {response.content}", Color.ENDC)
                    return False 
            except:
                print(f"{Color.FAIL}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} There is a error acoured on user/ping! Code: {response.status_code}", Color.ENDC)
                print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
                traceback.print_exc()
                return False
        else:
            print(f"{Color.FAIL}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} There is a error acoured on user/ping! Code: {response.status_code}", Color.ENDC)
            print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
            traceback.print_exc()
            return False 