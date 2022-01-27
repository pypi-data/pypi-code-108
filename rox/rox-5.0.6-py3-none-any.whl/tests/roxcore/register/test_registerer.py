import unittest

from rox.core.entities.flag import Flag
from rox.core.entities.rox_string import RoxString
from rox.core.register.registerer import Registerer
from rox.core.repositories.flag_repository import FlagRepository


class Container1:
    def __init__(self):
        self.rox_string = RoxString('1', ['1', '2', '3'])
        self.flag1 = Flag()
        self.flag2 = Flag()
        self.flag3 = Flag()

        self.something_else = object()


class RegistererTests(unittest.TestCase):
    def test_will_throw_when_ns_null(self):
        flag_repo = FlagRepository()
        container = Container1()
        registerer = Registerer(flag_repo)

        with self.assertRaises(TypeError):
            registerer.register_instance(container, None)

    def test_will_throw_when_ns_registered_twice(self):
        flag_repo = FlagRepository()
        container = Container1()
        registerer = Registerer(flag_repo)

        registerer.register_instance(container, 'ns1')

        with self.assertRaises(ValueError):
            registerer.register_instance(container, 'ns1')

    def test_will_register_variant_and_flag(self):
        flag_repo = FlagRepository()
        container = Container1()
        registerer = Registerer(flag_repo)

        registerer.register_instance(container, 'ns1')

        self.assertEqual(4, len(flag_repo.get_all_flags()))

        self.assertEqual('1', flag_repo.get_flag('ns1.rox_string').default_value)
        self.assertEqual('false', flag_repo.get_flag('ns1.flag1').default_value)

    def test_will_register_with_empty_ns(self):
        flag_repo = FlagRepository()
        container = Container1()
        registerer = Registerer(flag_repo)

        registerer.register_instance(container, '')

        self.assertEqual(4, len(flag_repo.get_all_flags()))

        self.assertEqual('1', flag_repo.get_flag('rox_string').default_value)
        self.assertEqual('false', flag_repo.get_flag('flag1').default_value)
