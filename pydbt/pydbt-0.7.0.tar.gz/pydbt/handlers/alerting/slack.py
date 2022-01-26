import logbook
import typing as T
from .base import BaseAlert
from ... import dbt_version
from ...types import Message, Freshness
from ...utils.http import make_external_call
from dbt.contracts.results import TimingInfo
from ...logger import logbook_status_to_color
from ...config import SUCCESS_ALERTS, ENV, NAME
from ...utils.tools import get_execution_datetime


class SlackAlert(BaseAlert):
    def __init__(self, url):
        super(SlackAlert, self).__init__()
        self.url = url
        self.success_alerts = SUCCESS_ALERTS

    @staticmethod
    def _get_issue_priority(level: int) -> str:
        if level == logbook.WARNING:
            return 'warning'

        if level in [logbook.ERROR, logbook.WARNING]:
            return 'high'

        return 'normal'

    @staticmethod
    def _get_message_body(
        title: str,
        message: str,
        error: str,
        attachment: T.Dict,
        timing: T.List[TimingInfo]
    ) -> T.Dict:
        return {
            **attachment, 'fallback': title,
            'title': title,
            'text': message if not error else message + f'\n ```{error}```',
            'ts': get_execution_datetime(timing)
        }

    def _get_freshness_attachment(self, attachment: T.Dict, fresh: Freshness) -> T.Dict:
        attachment['fields'].extend([{
            "title": "Loader",
            "value": fresh.loader,
            "short": True
        }, {
            "title": "Age",
            "value": f"{fresh.age} {fresh.unit}s",
            "short": True
        }])

        return attachment

    def _get_context_attachment(self, attachment: T.Dict, context: T.Dict) -> T.Dict:
        if 'path' in context:
            attachment['fields'].append({
                'title': 'Path',
                'value': context.get('path'),
                'short': True
            })

        if dbt_version:
            attachment = {
                **attachment,
                "footer": f"dbt {dbt_version}",
                "footer_icon": "https://www.getdbt.com/ui/img/graph/avatar.png",
            }

        # Add dbt tags
        if 'tags' in context:
            attachment['fields'].append(
                {"title": "Tags", "value": context.get('tags'), "short": True})

        return attachment

    def alert(self, msg: Message):
        status = logbook_status_to_color(msg.level)
        priority = self._get_issue_priority(msg.level)

        attachment = {
            "color": status,
            "fields": [
                {
                    "title": "Priority",
                    "value": priority.capitalize(),
                    "short": True
                },
                {
                    "title": "Environment",
                    "value": ENV,
                    "short": True
                },
            ],
        }

        if msg.reporting and msg.reporting.freshness:
            attachment = self._get_freshness_attachment(attachment, msg.reporting.freshness)

        attachment = self._get_context_attachment(attachment, msg.context)
        msg_body = self._get_message_body(msg.title, msg.message, msg.error, attachment, msg.reporting.timing)
        payload = {'attachments': [msg_body]}

        # Logic to block success messages if not requested
        if (msg.level < logbook.NOTICE) and not self.success_alerts:
            return

        return make_external_call(
            'POST',
            self.url,
            json=payload,
            timeout=30,
            service_name=NAME,
            raise_exception=True
        )
