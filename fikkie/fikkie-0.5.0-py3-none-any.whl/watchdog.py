import logging
import os

from .check import Check
from .config import load_config
from .notifiers import Notifier, Encoding


__all__ = ["WatchDog"]


class WatchDog:
    """
    Executes commands over SSH and notifies when the output is unexpected.

    Will keep track of the state to avoid excessive notification spamming.
    """

    def __init__(self):
        config = load_config()
        self._ssh_config: dict[str, str] = config.get("ssh", {})

        self.checks: list[Check] = [
            Check(h, self._ssh_config.get("username", "fikkie"), **c)
            for h, cs in config.get("servers", {}).items()
            for c in cs
        ]

        self._notifiers: list[Notifier] = [
            Notifier(**n) for n in config.get("notifiers", [])
        ]

    def notify(self, msg: str, icon: str = "") -> None:
        """Sends a notification using all available notifiers."""
        logging.info(f"Sending notification: {icon} {msg}")
        for notifier in self._notifiers:
            notifier.notify(
                f"{icon} {msg}" if notifier.ENCODING == Encoding.UTF8 and icon else msg
            )

    def tick(self) -> None:
        """Perform checks."""
        for check in self.checks:
            stdout_changed, stdout_expected, stdout, stderr = check.run()

            if stdout_changed:
                if stdout_expected:
                    self.notify(f"{check.host}: {check.description} OK", "🟢")
                else:
                    self.notify(
                        f"{check.host}: {check.description} NOT OK\n`{stdout}` (stderr: `{stderr}`)",
                        "🔴",
                    )

    def heartbeat(self) -> None:  # pragma: no cover - no complexity here
        """Send a notification to let user know the watchdog's alive."""
        self.notify("I'm still awake.", "❤️")
