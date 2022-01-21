import requests
import json

# Write by lyc at 2021-11-19
# V2021-11-19：


class Webhook_bot:

    def __init__(self, webhook_type, webhook_token) -> None:
        self.webhook_type = webhook_type
        self.webhook_token = webhook_token

    def send_webhook_msg(self, content_text):
        """[summary]

        Args:
            content_text ([string]): [description]
            webhook_type (string, optional): [description]. Defaults to ''.
            token (string, optional): [description]. Defaults to ''.

        Raises:
            Exception: [description]
        """

        if self.webhook_type == 'wechat':
            webhook_api_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={}".format(self.webhook_token)
        elif self.webhook_type == 'dingding':
            webhook_api_url="https://oapi.dingtalk.com/robot/send?access_token={}".format(self.webhook_token)
        else:
            raise Exception("\'webhook_type\' 必须是 wechat 或 dingding")

        headers = {'Content-Type': 'application/json;charset=utf-8'}
        json_data = {
        "msgtype": "text",
        "text": {
                "content": content_text
            }
        }
        requests.post(webhook_api_url, json.dumps(json_data), headers=headers)

