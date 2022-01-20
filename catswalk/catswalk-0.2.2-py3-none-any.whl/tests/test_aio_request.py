import asyncio
import aiohttp
import time
from bs4 import BeautifulSoup

websites = """https://www.youtube.com
https://www.facebook.com
https://www.baidu.com
"""


async def async_get(url, session):
    try:
        async with session.get(url=url) as response:
            resp = await response.read()
            print("Successfully got url {} with resp of length {}.".format(url, len(resp)))
            soup = BeautifulSoup(resp, features="html.parser")
            return soup
    except Exception as e:
        print("Unable to get url {} due to {}.".format(url, e.__class__))


async def async_gets(urls):
    async with aiohttp.ClientSession() as session:
        ret = await asyncio.gather(*[async_get(url, session) for url in urls])
    print(ret)
    print("Finalized all. Return is a list of len {} outputs.".format(len(ret)))


urls = websites.split("\n")
start = time.time()
asyncio.run(async_gets(urls))
end = time.time()

print("Took {} seconds to pull {} websites.".format(end - start, len(urls)))