from django.test import TestCase

from isc_common.auth.models.user import User
from tracker.models.messages import Messages
from tracker.models.messages_state import Messages_state
from tracker.models.messages_theme import Messages_theme


class Test_Messages(TestCase):

    def setUp(self):
        self.message = "message"
        self.user = User.objects.create_superuser(username="username", email="info@ivc-inform.ru", password="123")
        self.state = Messages_state.objects.get(code="new")
        self.theme = Messages_theme.objects.get(code="auto_from_error")

    def test_1(self):
        Messages_item = Messages.objects.create(message=self.message, user=self.user, state=self.state, theme=self.theme)
        Messages_item = Messages.objects.create(message=self.message, user=self.user, state=self.state, theme=self.theme)
        Messages_item = Messages.objects.get(pk=Messages_item.pk)

        self.assertEquals(Messages_item.message, self.message)
        self.assertEquals(Messages_item.user, self.user)
        self.assertEquals(Messages_item.state, self.state)
        self.assertEquals(Messages_item.theme, self.theme)
        print(f'checksum: {Messages_item.checksum}')

