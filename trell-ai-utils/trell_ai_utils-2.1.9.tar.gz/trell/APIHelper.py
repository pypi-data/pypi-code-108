import emoji
import requests
import json


def remove_emoji(text=None):
    if text:
        return emoji.get_emoji_regexp().sub(u'', text)
    else:
        return "Text is None"


def send_cron_alert(message):
    url = "https://hooks.slack.com/services/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"
    payload = {"text": message}
    requests.post(url=url, data=json.dumps(payload))


def send_ecommerce_alert(message):
    url = "https://hooks.slack.com/services/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"
    payload = {"text": message}
    requests.post(url=url, data=json.dumps(payload))


def send_alert(url, message):
    payload = {"text": message}
    requests.post(url=url, data=json.dumps(payload))


