import requests
import random

def UserAgent():
    useragents = requests.get("https://pastebin.com/raw/iqvMqytE").text.splitlines()
    chosen = random.choice(useragents)
    return chosen
