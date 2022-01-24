import pytest

from aleksis.core.models import Notification, Person

pytestmark = pytest.mark.django_db


def test_email_notification(mailoutbox):
    email = "doe@example.com"
    recipient = Person.objects.create(first_name="Jane", last_name="Doe", email=email)

    sender = "Foo"
    title = "There is happened something."
    description = "Here you get some more information."
    link = "https://aleksis.org/"

    notification = Notification(
        sender=sender, recipient=recipient, title=title, description=description, link=link
    )
    notification.save()

    assert notification.sent

    assert len(mailoutbox) == 1

    mail = mailoutbox[0]

    assert email in mail.to
    assert title in mail.body
    assert description in mail.body
    assert link in mail.body
    assert sender in mail.body
    assert recipient.addressing_name in mail.subject
    assert recipient.addressing_name in mail.body
