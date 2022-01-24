import requests

from config.settings import DING_ROBOT


class SendDingTalk:
    def __init__(self, robot):
        self.taskName = DING_ROBOT
        self.host = f"{DING_ROBOT[robot]['host']}?access_token={DING_ROBOT[robot]['token']}"

    def send_dingtalk_message(self, content):
        data = {'msgtype': 'text', 'text': {'content': '用户标签 ' + content}}
        response = None
        if isinstance(self.host, str):
            response = requests.post(self.host, json=data)
        else:
            for url in self.host:
                response = requests.post(url, json=data)
        return response


def send_dingtalk_message(message='', channel='default'):
    SendDingTalk(channel).send_dingtalk_message(message)


if __name__ == '__main__':
    SendDingTalk('default').send_dingtalk_message("你好")
