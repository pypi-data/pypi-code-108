import requests


def gg_gg(url: str, custom_path: str = 'dofast') -> str:
    # gg.gg url shortener
    params = {
        'long_url': url,
        'custom_path': custom_path,
        'use_norefs': 0,
        'app': 'site',
        'version': 0.1
    }
    host = 'http://gg.gg/create'
    return requests.post(host, data=params).text
