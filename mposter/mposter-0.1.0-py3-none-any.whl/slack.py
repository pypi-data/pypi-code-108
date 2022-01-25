from slackclient import SlackClient
from mposter import http


def chat_post(slack_token: str, message: str, owner_slack: str, ts: str = None, proxies: dict = None) -> dict:
    try:
        if proxies is None:
            proxies = http.get_proxies_v2(paid_type='paid')

        client = SlackClient(slack_token, proxies=proxies)

        result = client.api_call(
            "chat.postMessage",
            as_user=True,
            channel=owner_slack,
            text=message,
            thread_ts=ts
        )

        return result
    except Exception as ex:
        print('chat_post', ex)
