import datetime
import json

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django_redis import get_redis_connection

from notifications.models import Notification, UserNotification
from timonutils.tests.base import BaseClientTest

User = get_user_model()


class NotificationTest(BaseClientTest):
    SNOOZE_TIME = 1

    def setUp(self):
        self.tearDown()
        super(NotificationTest, self).setUp()
        self.notification = Notification.objects.create(
            name_en="test",
            name_is="test",
            message_en="test message",
            message_is="test message",
            snooze_time=self.SNOOZE_TIME
        )
        self.user = User.objects.get(username=self.USERNAME)
        self.un = UserNotification.objects.create(notification=self.notification, user=self.user)
        self.created = datetime.datetime.now()

    def tearDown(self):
        get_redis_connection("default").flushall()

    def test_creation(self):
        self.assertEqual(len(Notification.unseen(self.user)), 1)

    def test_seen(self):
        self.un.seen = True
        self.un.answer = True
        self.un.save()
        self.assertEqual(len(Notification.unseen(self.user)), 0)
        self.un.answer = False
        self.un.save()
        self.assertEqual(len(Notification.unseen(self.user)), 1)

    def test_cookie(self):
        response = self.client.get('/api/')
        notification_cookie = response.cookies['notifications'].value.split(':')
        unseenid = notification_cookie[0]
        self.assertEqual(int(unseenid), self.un.id)
        unseentime = float(notification_cookie[1]) / 1000

        utcfromtimestamp = datetime.datetime.utcfromtimestamp(unseentime)
        self.assertTrue(abs(utcfromtimestamp - self.created) < datetime.timedelta(seconds=5, minutes=10))

        self.un.seen = True
        self.un.answer = False
        self.un.save()
        snooze = datetime.datetime.now() + datetime.timedelta(days=self.SNOOZE_TIME)
        response = self.client.get('/api/')
        notification_cookie = response.cookies['notifications'].value.split(':')
        unseenid = notification_cookie[0]
        self.assertEqual(int(unseenid), self.un.id)
        unseentime = float(notification_cookie[1]) / 1000
        self.assertTrue(abs(datetime.datetime.utcfromtimestamp(unseentime) - snooze) < datetime.timedelta(seconds=1))

    def test_expired(self):
        response = self.client.get('/api2/usernotifications/')
        self.assertEqual(len(json.loads(response.content)), 1)
        self.notification.expires = datetime.datetime.now() - datetime.timedelta(1)
        self.notification.save()

        response = self.client.get('/api2/usernotifications/')
        self.assertEqual(len(json.loads(response.content)), 0)

        # Make sure model interface returns same as api
        self.assertEqual(len(Notification.unseen(self.user)), 0)

    def test_deletion(self):
        self.un.delete()
        self.assertEqual(len(Notification.unseen(self.user)), 0)

    def test_group_creation(self):
        self.un.delete()
        self.assertEqual(len(Notification.unseen(self.user)), 0)
        group = Group.objects.last()
        self.user.groups.add(group)
        self.notification.groups.add(group)
        self.notification.create_usernotifications_for_groups()
        self.assertEqual(len(Notification.unseen(self.user)), 1)

        # No duplicates
        self.notification.groups.add(group)
        self.assertEqual(len(Notification.unseen(self.user)), 1)
