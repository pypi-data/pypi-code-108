import random
import requests


def get_proxies():
    return None
    return {'http': 'socks5://127.0.0.1:8389', 'https': 'socks5://127.0.0.1:8389'}


def get_ua():
    return  random.choice([
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"])


def get_html(data=None):
    headers = {"User-Agent": get_ua(), "sec-ch-ua": "\"Chromium\";v=\"92\", \" Not A;Brand\";v=\"99\", \"Google Chrome\";v=\"92\"", "sec-ch-ua-mobile": "?0", "Host": "warehouse-camo.ingress.cmh1.psfhosted.org", "Referer": "https://pypi.org/", "Origin": "https://pypi.org", "Connection": "keep-alive"}
    res = requests.get(
        url=r"https://warehouse-camo.ingress.cmh1.psfhosted.org/b611884ff90435a0575dbab7d9b0d3e60f136466/68747470733a2f2f73746f726167652e676f6f676c65617069732e636f6d2f707970692d6173736574732f73706f6e736f726c6f676f732f737461747573706167652d77686974652d6c6f676f2d5467476c6a4a2d502e706e67",
        headers=headers,
        verify=False,
        # stream=True,
        stream=False,
        proxies=get_proxies(),
        timeout=125,
    )
    return res.text


if __name__ == '__main__':
    print(get_html())
