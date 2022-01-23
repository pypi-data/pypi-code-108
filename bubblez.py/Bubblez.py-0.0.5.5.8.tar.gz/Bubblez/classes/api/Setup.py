from ..Color import Color
from ..Log import logTime

import requests, json 

class Setup:
    def __init__(self, client) -> None:
        self.client = client 

    def login(self):
        if not self.client.token:
            print(f"{Color.FAIL}[Bubblez.py-{self.client.prefix_log}] {logTime()} Token missing! {Color.ENDC}")
            quit()
        data, _url = {}, "/user/check"
        if self.client.canary: url = self.client.canary_url + _url
        else: url = self.client.live_url + _url 
        data['token'] = self.client.token
        response = requests.post(url=url, data=data)
        if response.ok:
            try:
                js =  response.json()
                print(f"{Color.OKGREEN}[Bubblez.py-{self.client.prefix_log}] {logTime()} Welkom {js['displayname']}, You are logged in!{Color.ENDC}")
                return js
            except:
                print(f"{Color.FAIL}[Bubblez.py-{self.client.prefix_log}] {logTime()} Could not login!, Status Code: {response.status_code} {Color.ENDC}")
                print(f"{Color.FAIL}Server response:", response.content, Color.ENDC)
                quit()
        print(f"{Color.FAIL}[Bubblez.py-{self.client.prefix_log}] {logTime()} Could not login!{Color.ENDC}")
        print(f"{Color.FAIL} Status code:", response.status_code, Color.ENDC)
        quit()