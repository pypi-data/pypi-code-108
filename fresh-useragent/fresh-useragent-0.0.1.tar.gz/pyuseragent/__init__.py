import requests
import random

useragents = requests.get("https://pastebin.com/raw/iqvMqytE").text.splitlines()
def UserAgent():
    useragent = random.choice(useragents)
    return useragent