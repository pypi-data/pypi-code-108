import unittest

from rox.core.configuration.models.target_group_model import TargetGroupModel
from rox.core.repositories.target_group_repository import TargetGroupRepository


class TargetGroupRepositoryTests(unittest.TestCase):
    def test_will_return_null_when_not_found(self):
        tgs = [TargetGroupModel('1', 'x')]
        tg_repo = TargetGroupRepository()
        tg_repo.set_target_groups(tgs)

        self.assertIsNone(tg_repo.get_target_group('2'))

    def test_will_return_when_found(self):
        tgs = [TargetGroupModel('1', 'x')]
        tg_repo = TargetGroupRepository()
        tg_repo.set_target_groups(tgs)

        self.assertEqual('x', tg_repo.get_target_group('1').condition)
