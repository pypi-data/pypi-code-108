import json
import aiohttp
import asyncio

class DistMLLogger:
    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.api_endpoint = ""
        self.payload = ""

    def printLoggerConfig(self):
        print('api_endpoint %s ' % self.api_endpoint)
        print('payload %s ' % self.payload)

    def setup(self):
        #read metadata
        with open('/var/log/distml/metadata/distml.json') as f:
            data = json.load(f)
            self.api_endpoint = data['distml_api_endpoint']

    def logit(self, data):
        # using asyncio to send it
        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_endpoint, json=data) as resp:
                response = await resp.text()

