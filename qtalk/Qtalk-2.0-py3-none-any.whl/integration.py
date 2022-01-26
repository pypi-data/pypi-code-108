import json
import os
#import sys
import requests

# for local development:
# sys.path.append(os.getcwd())  
# # LOADS config.json file
# working_directory = os.getcwd()
# # with open(working_directory+'/tools/webhook_config.json', 'r') as c:
# #     wh_data = c.read()
# # webhook_config = json.loads(wh_data)
# from dotenv import load_dotenv
# load_dotenv()

class Singleton(type):

    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(cls, bases, dict)
        cls._instanceDict = {}

    def __call__(cls, *args, **kwargs):
        argdict = {'args': args}
        argdict.update(kwargs)
        argset = frozenset(argdict)
        if argset not in cls._instanceDict:
            cls._instanceDict[argset] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instanceDict[argset]


class Mattermost(metaclass=Singleton):

    def __init__(self):
        pass

    def publish_message(self,**kwargs):
        
        webhook = os.environ["QTALK_QUANTICO_WEBHOOK"]
        channel = os.environ["QTALK_QUANTICO_CHANNEL"]
        
        title = '### :rotating_light: Alerta de Quantico Connect'
        title = title + '\n'

        header = [f'|{key}' for key in kwargs['text'].keys()]
        header = "".join(header)
        header = header + "| \n"
        
        separator = [f'|:---' for item in kwargs['text']]
        separator = "".join(separator)
        separator = separator + "| \n"

        content = [f'|{value}' for value in kwargs['text'].values()]
        content = "".join(content)
        content = content + "| \n"
        
        text = title + header + separator + content
        payload = {"text": text, "channel": channel}
        response = requests.post(webhook, data=json.dumps(payload),verify=True)
        if response.status_code==200:
            print("== SUCCESS: MESSAGE NOTIFICATED ==", flush=True)
        else:
            print("== WARNING: ERROR PUBLISHING MESSAGE ON MATTERMOST ==", response.json(), flush=True)
        return
