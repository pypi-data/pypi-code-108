import asyncio
import aiohttp
from bs4 import BeautifulSoup
import logging

class AsyncRequestException(Exception):
    pass



async def async_get(url, session):
    try:
        async with session.get(url=url) as response:
            if response.status != 200:
                raise AsyncRequestException(f"status is {response.status}, {url}")
            resp = await response.read()
            logging.info("Successfully got url {} with resp of length {}.".format(url, len(resp)))
            soup = BeautifulSoup(resp, features="html.parser")
            return soup
    except Exception as e:
        logging.error("Unable to get url {} due to {}.".format(url, e.__class__))


async def async_gets(url_list):
    async with aiohttp.ClientSession() as session:
        ret = await asyncio.gather(*[async_get(url, session) for url in url_list])
    logging.info("Finalized all. Return is a list of len {} outputs.".format(len(ret)))
    return ret


class AsyncCWRequest:
    @classmethod
    def execute(self, url_list):
        result = asyncio.run(async_gets(url_list))
        return result