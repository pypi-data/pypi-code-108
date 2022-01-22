import json
import os
import time
import hmac
import hashlib
import base64
import urllib.parse
import requests

from ..config.config_client import ConfigClient

LIB_APP_ID = "winhye_common"
app_id = os.environ.get("APP_ID", "NOT_EXIST")
if app_id == "NOT_EXIST":
    app_id = LIB_APP_ID
ConfigClient.init(app_id)


class DingAlarm:
    def __init__(self):
        alarm_conf = ConfigClient.get_configger("winhye_software.common")
        alarm_config = alarm_conf.get_group("alarm")
        self.secret = alarm_config.secret
        self.url = alarm_config.url
        self.atMobiles = json.loads(alarm_config.atMobiles)
        self.isAtAll = eval(alarm_config.isAtAll)

    def get_sign(self):
        timestamp = str(round(time.time() * 1000))
        secret_enc = self.secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, self.secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return timestamp, sign

    def send_alarm_message(self, msg):
        timestamp, sign = self.get_sign()
        url = f"{self.url}&timestamp={timestamp}&sign={sign}"

        message = {
            "msgtype": "text",
            "text": {
                "content": f"报错信息：\n{msg}"
            },
            "at": {  # @的人
                "atMobiles": self.atMobiles,  # 钉钉的电话号码
                "atUserIds": [],
                "isAtAll": self.isAtAll
            }
        }
        requests.post(url, json=message)


ding_alarm = DingAlarm()
