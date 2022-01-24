import json
import aiohttp
import asyncio

class distml_logger:
    def __init__(self):
        ''' Constructor for this class. '''
        # Create some member animals
        self.api_endpoint = ""
        self.payload = ""

    def distml_print(self):
        print('api_endpoint %s ' % self.api_endpoint)
        print('payload %s ' % self.payload)

    def distml_setup(self):
        #read metadata
        with open('/var/log/distml/metadata/distml.json') as f:
            data = json.load(f)
            self.api_endpoint = data['distml_api_endpoint']

    async def distml_logit(self, data):
        # using asyncio to send it
        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_endpoint, json=data) as resp:
                response = await resp.text()
                print("distml server response %s" % response)

