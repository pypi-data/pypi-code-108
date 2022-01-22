from asyncio import get_running_loop, AbstractEventLoop
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import partial
from logging import LogRecord, Handler, NOTSET
from typing import Optional, List

from requests import Session


class DiscordWebhookHandler(Handler):
    """A logging handler that allows you to send messages with Discord Webhooks."""

    def __init__(
            self,
            webhook: str,
            level: int = NOTSET,
            *,
            session: Optional[Session] = None,
            can_format: bool = False,
            can_run_async: bool = True,
            executor: Optional[ThreadPoolExecutor] = None,
    ):
        super().__init__(level)
        self._webhook: str = webhook
        self._new_client: bool = session is None
        self._session: Session = session or Session()
        self._format: bool = can_format
        self._can_run_async: bool = True
        self._executor: Optional[ThreadPoolExecutor] = None

    def close(self) -> None:
        self._session.post(self._webhook, json={
            "content": "**CLOSED**"
        })
        if self._new_client:
            self._session.close()

    def emit(self, record: LogRecord) -> None:
        if record.levelname == "CRITICAL" or record.levelname == "FATAL" or record.levelname == "ERROR":
            color: int = 0xFF0000
        elif record.levelname == "WARN" or record.levelname == "WARNING":
            color: int = 0xFFFF00
        elif record.levelname == "DEBUG":
            color: int = 0x5a0d36  # picked from my oneshot banner because its eye-catching
        else:
            color: int = 0xFFFFFF

        partial_post: partial = partial(self._session.post, self._webhook, json={
            "embeds": [
                {
                    "title": f"{record.levelname} on {record.threadName} ({record.thread})",
                    "color": color,
                    "description": f"```{self.format(record) if self._format else record.getMessage()}```",
                    "timestamp": datetime.utcfromtimestamp(record.created).isoformat(),
                    "footer": {
                        "text": record.name
                    }
                }
            ]
        })

        try:
            maybe_running_loop: Optional[AbstractEventLoop] = get_running_loop()
        except RuntimeError:
            maybe_running_loop: Optional[AbstractEventLoop] = None
        except Exception:
            raise

        if self._can_run_async and maybe_running_loop is not None:
            maybe_running_loop.run_in_executor(self._executor, partial_post)
        else:
            partial_post()


__all__: List[str] = [
    "DiscordWebhookHandler"
]
