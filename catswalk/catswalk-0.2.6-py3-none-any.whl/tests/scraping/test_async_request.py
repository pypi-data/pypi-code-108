import asyncio
import aiohttp
import time
from bs4 import BeautifulSoup
from catswalk.scraping.async_request import  AsyncCWRequest

url_list = ["https://www.youtube.com", "https://www.facebook.com", "https://www.baidu.com"]

AsyncCWRequest.execute(url_list)