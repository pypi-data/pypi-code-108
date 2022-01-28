from django.db import IntegrityError
from django.test import TestCase
from isc_common.auth.models.usergroup import UserGroup


class Test_UserGroup(TestCase):

    def setUp(self):
        self.code = "code"
        self.name = "name"
        self.description = "description"

    def test_1(self):
        UserGroup_item = UserGroup.objects.create(code=self.code, name=self.name, description=self.description)
        UserGroup_item = UserGroup.objects.get(pk=UserGroup_item.pk)
        self.assertEquals(UserGroup_item.code, self.code)
        self.assertEquals(UserGroup_item.name, self.name)
        self.assertEquals(UserGroup_item.description, self.description)

        self.code += '1'
        UserGroup_item = UserGroup.objects.create(code=self.code, name=self.name)
        UserGroup_item = UserGroup.objects.get(pk=UserGroup_item.pk)
        self.assertEquals(UserGroup_item.code, self.code)
        self.assertEquals(UserGroup_item.name, self.name)
        self.assertEquals(UserGroup_item.description, None)

        self.code += '1'
        UserGroup_item = UserGroup.objects.create(code=self.code)
        UserGroup_item = UserGroup.objects.get(pk=UserGroup_item.pk)
        self.assertEquals(UserGroup_item.code, self.code)
        self.assertEquals(UserGroup_item.name, None)
        self.assertEquals(UserGroup_item.description, None)

    def test_2(self):
        with self.assertRaises(AssertionError):
            UserGroup_item = UserGroup.objects.create()

    def test_3(self):
        with self.assertRaises(IntegrityError):
            UserGroup_item = UserGroup.objects.create(code=self.code)
            UserGroup_item = UserGroup.objects.create(code=self.code)

