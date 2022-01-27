import unittest

from rox.core.entities.flag import Flag
from rox.core.repositories.flag_repository import FlagRepository


class FlagRepositoryTests(unittest.TestCase):
    def test_will_return_null_when_flag_not_found(self):
        repo = FlagRepository()

        self.assertIsNone(repo.get_flag('harti'))

    def test_will_add_flag_and_set_name(self):
        repo = FlagRepository()
        flag = Flag()
        repo.add_flag(flag, 'harti')

        self.assertEqual('harti', repo.get_flag('harti').name)

    def test_will_raise_flag_added_event(self):
        repo = FlagRepository()
        flag = Flag()
        variant_from_event = {'variant': None}

        def flag_added(variant):
            variant_from_event['variant'] = variant

        repo.register_flag_added_handler(flag_added)
        repo.add_flag(flag, 'harti')

        self.assertEqual('harti', variant_from_event['variant'].name)
