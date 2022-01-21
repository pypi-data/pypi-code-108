from askbot.models import Role, User
from askbot.models.role import ADMIN_ROLES, MOD_ROLES
from askbot.tests.utils import AskbotTestCase

class RoleTests(AskbotTestCase):
    def test_admin_roles(self):
        u = self.create_user(status='d')
        self.assertEqual(u.get_roles(), ADMIN_ROLES)

    def test_demoted_admin_roles(self):
        u = self.create_user(status='d')
        u.set_status('a')
        self.assertEqual(u.get_roles(), set())

    def test_mod_roles(self):
        u = self.create_user(status='m')
        self.assertEqual(u.get_roles(), MOD_ROLES)

    def test_demoted_mod_roles(self):
        u = self.create_user(status='m')
        u.set_status('a')
        self.assertEqual(u.get_roles(), set())

    def test_mod_to_admin_roles(self):
        u = self.create_user(status='m')
        u.set_status('d')
        self.assertEqual(u.get_roles(), ADMIN_ROLES)

    def test_admin_to_mod_roles(self):
        u = self.create_user(status='d')
        u.set_status('m')
        self.assertEqual(u.get_roles(), MOD_ROLES)

    def test_assign_role_set(self):
        u = self.create_user(status='d')
        # test reassigning the same roles over the existing ones
        # without db integrity errors
        u.assign_role_set('administrator')
        self.assertEqual(u.get_roles(), ADMIN_ROLES)
