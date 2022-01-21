import logging
import smtplib
import ssl


__all__ = ["EmailNotifier"]


class EmailNotifier:
    """An e-mail notifier."""

    TYPE = "email"
    ENCODING = "ASCII"

    def __init__(
        self,
        recipient: str,
        email: str,
        password: str,
        smtp_server: str,
        smtp_port: int = 465,
    ):
        self._recipient = recipient
        self._email = email
        self._password = password
        self._smtp_server = smtp_server
        self._smtp_port = smtp_port

    def notify(self, text: str) -> None:
        """Sends a message."""
        message = f"""Subject: {text}

        Fikkie wants to notify you about the following message:

        {text}
        """

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(
            self._smtp_server, self._smtp_port, context=context
        ) as server:
            server.login(self._email, self._password)
            server.sendmail(self._email, self._recipient, message)
