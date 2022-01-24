import json
import requests

def send(url, key, params):
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Authorization": key,
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36",
    }
    response = requests.post(url, data=json.dumps(params), headers=headers)
    if response.status_code == requests.codes.ok:
        return response.text