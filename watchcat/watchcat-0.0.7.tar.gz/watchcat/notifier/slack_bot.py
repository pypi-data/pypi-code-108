import sys
from watchcat.notifier.errors import NotificationError
from .notifier import Notifier
import requests


class SlackBotNotifier(Notifier):
    def __init__(self, _id: str, token: str, channel: str) -> None:
        super().__init__(_id)
        self.token = token
        self.channel = channel

    def send(self, title: str, description: str, diff: str):
        res = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={"content-type": "application/json", "authorization": f"Bearer {self.token}"},
            json={
                "channel": self.channel,
                "unfurl_media": True,
                "text": title,
                "blocks": [
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": f"*{title}*\n{description}"},
                    }
                ],
            },
        )
        if res.status_code != 200 or res.json()["ok"] == False:
            print(res.status_code)
            print(res.text, file=sys.stderr)
            raise NotificationError()

        res = requests.post(
            "https://slack.com/api/files.upload",
            headers={"content-type": "application/x-www-form-urlencoded", "authorization": f"Bearer {self.token}"},
            data={"channels": self.channel, "content": diff, "filetype": "diff", "title": title},
        )
        if res.status_code != 200 or res.json()["ok"] == False:
            print(res.status_code)
            print(res.text, file=sys.stderr)
            raise NotificationError()

    def __str__(self) -> str:
        return f"<SlackBotNotifier(token=***, channel={self.webhook_url})>"
