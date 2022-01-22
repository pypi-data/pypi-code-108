from os import getenv
import pathlib

from dotenv import load_dotenv
from redmail import EmailSender

load_dotenv()

MAILER = EmailSender(
    getenv("SMTP_SERVER"),
    port=getenv("SMTP_PORT"),
    user_name=getenv("SMTP_USERNAME"),
    password=getenv("SMTP_PASSWORD"),
)
BCCS = getenv("EMAIL_BCCS").split(";")


def send_mail(
    recipients, subject, body, attachments=[], to=getenv("EMAIL_SENDER"), bccs=BCCS
):
    if not hasattr(recipients, "extend"):
        recipients = [recipients]
    MAILER.send(
        sender=to,
        receivers=recipients,
        bcc=bccs,
        subject=subject,
        html=body,
        attachments=attachments,
    )


if __name__ == "__main__":
    send_mail(
        "vanwykk@gmail.com",
        "Testing",
        "This is the body",
        attachments=[
            pathlib.Path("data.json"),
        ],
    )
