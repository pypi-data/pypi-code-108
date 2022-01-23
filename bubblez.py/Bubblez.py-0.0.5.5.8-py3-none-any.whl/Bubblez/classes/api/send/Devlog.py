from requests.models import DecodeError
from ...Color import Color
from ...Log import logTime
from ..receive.Devlog import Devlog as ResponseDevlog

import requests, traceback

class Devlog:
    def __init__(self, client) -> None:
        self.client = client

    def get_latest(self):
        """ Get the latest Devlog 
        """
        data, url = {"token": self.client.token}, self.client.live_url
        if self.client.canary: url = self.client.canary_url
        url += "/blog/latest"
        response = requests.post(url=url, data=data)
        if response.ok:
            try:
                resp_js = response.json()
                if '200' in resp_js:
                    if resp_js['200'] == f'latest Blog Post':
                        print(f"{Color.OKGREEN}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} Got latest Devlog/Blog {Color.ENDC}")
                        return ResponseDevlog(self.client, resp_js)
                else:
                    print(f"{Color.WARNING}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} Did not found the latest Devlog! Code: {response.status_code}", Color.ENDC)
                    print(f"{Color.WARNING}Reason: {response.content}", Color.ENDC)
                    return False 
            except:
                print(f"{Color.FAIL}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} There is a error acoured on devlog/get_latest! Code: {response.status_code}", Color.ENDC)
                print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
                traceback.print_exc()
                return False 
        else:      
            print(f"{Color.FAIL}[Bubblez.py-api-{self.client.prefix_log}] {logTime()} There is a error acoured on devlog/get_latest! Code: {response.status_code}", Color.ENDC)
            print(f"{Color.FAIL}Reason: {response.content}", Color.ENDC)
            traceback.print_exc()
            return False 