from django.db import IntegrityError
from django.test import TestCase
from isc_common.auth.models.user import User
from isc_common.auth.models.usergroup import UserGroup


class Test_User(TestCase):

    def setUp(self):
        self.passwqord = "passwqord"
        self.username = "username"
        self.password = "username"
        self.email = "info@ivc-inform.ru"
        self.first_name = "first_name"
        self.last_name = "last_name"
        self.middle_name = "middle_name"
        self.group = UserGroup.objects.get(code='administrators')

    def test_1(self):
        User_item = User.objects.create_superuser(username=self.username, password=self.password, email=self.email)
        User_item = User.objects.get(pk=User_item.pk)
        self.assertTrue(User_item.has_usable_password())
        self.assertFalse(User_item.check_password('bad'))
        self.assertTrue(User_item.check_password(self.password))

        self.username += '1'
        User_item = User.objects.create_superuser(
            username=self.username,
            password=self.password,
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
            middle_name=self.middle_name,
        )
        User_item = User.objects.get(pk=User_item.pk)
        self.assertTrue(User_item.check_password(self.password))
        self.assertEquals(User_item.first_name, self.first_name)
        self.assertEquals(User_item.last_name, self.last_name)
        self.assertEquals(User_item.middle_name, self.middle_name)

    def test_2(self):
        with self.assertRaises(IntegrityError):
            User.objects.create_superuser(username=self.username, password=self.password, email=self.email)
            User.objects.create_superuser(username=self.username, password=self.password, email=self.email)

    def test_3(self):
        with self.assertRaises(IntegrityError):
            User.objects.create()

    def test_4(self):
        group1 = UserGroup.objects.create(code="group1")
        group2 = UserGroup.objects.create(code="group2")
        User_item = User.objects.create_user(usergroup= [group1, group2], username=self.username, password=self.password)
        User_item = User.objects.get(pk=User_item.pk)
        groups = User_item.usergroup.all()
        for group in groups:
            print(group)
        self.assertTrue(User_item.has_usable_password())
        self.assertTrue(User_item.check_password(self.password))

