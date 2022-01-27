import requests


def shorten_url(url: str):
    params = {
        'long_url': url,
        'custom_path': '',
        'use_norefs': 0,
        'app': 'site',
        'version': 0.1
    }
    host = 'http://gg.gg/create'
    return requests.post(host, data=params).text
