from django.test import TestCase

from exo_role.models import ExORole, CertificationRole, Category


class TestMigrationsTestCase(TestCase):

    def test_create_initial_exo_roles(self):
        # PREPARE DATA
        categories = Category.objects.all()

        # PRE ASSERTS
        self.assertTrue(categories.exists())

        # ASSERTS
        for category in categories:
            self.assertTrue(ExORole.objects.all().filter_by_category(category).exists())

    def test_create_initial_certification_roles(self):

        # ASSERTS
        self.assertTrue(CertificationRole.objects.all().exists())
