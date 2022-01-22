import json
import requests
from pyocs.pyocs_login import PyocsLogin
import base64
import pprint


def common_request(method, url, **kwargs):
    cookies = PyocsLogin().get_login_cookies_str()
    cookies_bs64 = base64.b64encode(cookies.encode())
    headers = {
        "cookies": cookies_bs64
    }
    ret = requests.request(method=method, url=url, headers=headers, **kwargs)
    return ret


def search_software(sw_info):
    faas_url = "https://faas.gz.cvte.cn/function/order-search-software"
    payload = json.dumps({
        "sw_info": sw_info
    })
    response = common_request("GET", faas_url, data=payload)
    print(response.json())
    return response.json()['data']


def refresh_software_link_by_attachment_id(attachment_id):
    url = "https://faas.gz.cvte.cn/function/order-refresh-software-link"
    payload = json.dumps({
        "attachment_id": attachment_id
    })
    response = common_request("GET", url, data=payload)
    print(response.json())
    return response.json()['data']


def refresh_software_link_by_sw_info(sw_info):
    url = "https://faas.gz.cvte.cn/function/order-refresh-software-link"
    payload = json.dumps({
        "sw_info": sw_info
    })
    response = common_request("GET", url, data=payload)
    print(response.json())
    return response.json()['data']


def get_software_list(ocs_number, exclude_disable=True, exclude_bin=True, exclude_lock=True, use_cache=True):
    faas_url = "https://faas.gz.cvte.cn/function/order-get-software-list"
    exclude_disable = "true" if exclude_disable else "false"
    exclude_bin = "true" if exclude_bin else "false"
    exclude_lock = "true" if exclude_lock else "false"
    use_cache = "true" if use_cache else "false"
    data = json.dumps({
        "ocs": ocs_number,
        "exclude_disable": exclude_disable,
        "exclude_bin": exclude_bin,
        "exclude_lock": exclude_lock,
        "use_cache": use_cache
    })
    ret = common_request("GET", faas_url, data=data)
    return ret.json()["data"]


def copy_software(src, dst):
    url = "https://faas.gz.cvte.cn/function/order-copy-software"
    payload = json.dumps({
        "src": src,
        "dst": dst
    })
    ret = common_request("GET", url, data=payload)
    pprint.pprint(ret.json()['data'])
    return ret.json()["data"]


if __name__ == '__main__':
    # search_software("20201118_195056")
    # refresh_software_link_by_attachment_id("5fb51e9a-13a0-4148-b238-6da6ac11527a")
    ret = get_software_list(ocs_number="641420", exclude_disable=False, exclude_bin=False, exclude_lock=False)
    print(ret)
