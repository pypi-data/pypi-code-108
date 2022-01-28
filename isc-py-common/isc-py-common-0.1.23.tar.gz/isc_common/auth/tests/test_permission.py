from django.test import TestCase

from isc_common.auth.models.user import User
from isc_common.auth.models.widgets_trees import Widgets_trees


class Test_Permission(TestCase):

    def setUp(self):
        self.user = User.objects.get(username='admin')
        self.widget = Widgets_trees.objects.get(id_widget='MainNitelArchive_DataViewSS')

    def test_1(self):
        grouops = self.user.usergroup.all()
        print('Hello World !!!')
