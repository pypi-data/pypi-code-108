import re
import time
from pprint import pprint
import requests
from logzero import logger


# 基于atxserver远程调用真机
class Device(object):
    def __init__(self, server_url, token):
        self.server_url = server_url
        self.token = token
        self.udid = None
        self.address = None

    def mark_url(self, path):
        if re.match(r"^https?://", path):
            return path
        return self.server_url + path

    def request_api(self, path, method="GET", **kwargs):
        kwargs['headers'] = {"Authorization": "Bearer " + self.token}
        r = requests.request(method, self.mark_url(path), **kwargs)
        try:
            r.raise_for_status()
        except requests.HTTPError:
            pprint(r.text)
        return r.json()

    def get_device(self, platform='android'):
        # 获取用户信息
        ret = self.request_api("/api/v1/user")
        logger.info(f"User: {ret['username']}")

        # 获取可用设备列表
        ret = self.request_api("/api/v1/devices", params={"usable": "true", "platform": platform})
        # logger.info(ret)
        if not ret['devices']:
            raise EnvironmentError("No devices")
        logger.info(f"Device count: {len(ret['devices'])}")

        # 占用设备
        device = ret['devices'][1]
        self.udid = device['udid']
        logger.info(f"Choose device: {device['properties']['name']} udid={self.udid}")
        ret = self.request_api("/api/v1/user/devices", method='post', json={"udid": self.udid})
        # logger.info(ret)

        # 获取占用设备信息
        ret = self.request_api("/api/v1/user/devices/" + self.udid)
        source = ret['device']['source']
        pprint(source)
        if platform == 'android':
            self.address = source['atxAgentAddress']
            # subprocess.run(['adb', 'connect', self.address])
            time.sleep(1)
        if platform == 'apple':
            self.address = source['wdaUrl']
        return self.address

    def release_device(self):
        # subprocess.run(['adb', 'disconnect', self.address])
        ret = self.request_api("/api/v1/user/devices/" + self.udid, method="delete")
        print(ret)



