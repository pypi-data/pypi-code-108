import sys
from watchcat.notifier.errors import NotificationError
from .notifier import Notifier
import requests


class SlackWebhookNotifier(Notifier):
    def __init__(self, _id: str, webhook_url: str) -> None:
        super().__init__(_id)
        self.webhook_url = webhook_url

    def send(self, title: str, description: str, diff: str):
        res = requests.post(
            self.webhook_url,
            json={
                "text": title,
                "blocks": [
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": f"*{title}*\n{description}\n\n```\n{diff}\n```"},
                    }
                ],
            },
        )
        if res.status_code == 200:
            return
        else:
            print(res.text, file=sys.stderr)
            raise NotificationError()

    def __str__(self) -> str:
        return f"<SlackWebhookNotifier(webhook_url={self.webhook_url})>"
