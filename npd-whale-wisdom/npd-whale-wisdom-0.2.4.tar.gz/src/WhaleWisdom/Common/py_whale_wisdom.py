import hashlib
import hmac
import time
import base64
from urllib.parse import quote_plus
import certifi
import requests
import os

secret_key = os.getenv("WW_SECRET_KEY")
shared_key = os.getenv("WW_SHARED_KEY")

def call_api(json_args):

    #pulled from Whale Wisdom Python example
    formatted_args = quote_plus(json_args)
    timenow = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    digest = hashlib.sha1
    raw_args=json_args+'\n'+timenow
    hmac_hash = hmac.new(secret_key.encode(),raw_args.encode(),digest).digest()
    sig = base64.b64encode(hmac_hash).rstrip()
    url_base = 'https://whalewisdom.com/shell/command.json?'
    url_args = 'args=' + formatted_args
    url_end = '&api_shared_key=' + shared_key + '&api_sig=' + sig.decode() + '&timestamp=' + timenow
    api_url = url_base + url_args + url_end

    #use requests instead of pycurl, breaking from example
    res = requests.get(api_url)
    return res.json()


def get_quarter(quarter):
    #gets the quarter ID for the given end of quarter date
    quarters = call_api('{"command":"quarters"}')
    if quarter == None:
        return quarters["quarters"][-1]["id"]
    else:
        quarter = quarter.replace("-","/")
        for q in quarters["quarters"]:
            if q["filing_period"] == quarter:
                return q["id"]
    return None