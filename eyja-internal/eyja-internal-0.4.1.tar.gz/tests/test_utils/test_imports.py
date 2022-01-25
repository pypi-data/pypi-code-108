from unittest import TestCase

from eyja.utils import load_class


class ImportTest(TestCase):
    def test_load_class(self):
        test_class_1 = load_class('tests.packages.dynamic_class_import.TestClass')
        test_class_2 = load_class('tests.packages.dynamic_class_import.test_module.Test2Class')
        test_class_3 = load_class('tests.packages.dynamic_class_import.test_module.test_submodule.Test3Class')
        test_class_4 = load_class('tests.packages.dynamic_class_import.test_module.test_submodule.Test4Class')

        self.assertEqual(test_class_1.name, 'test')
        self.assertEqual(test_class_2.name, 'test2')
        self.assertEqual(test_class_3.name, 'test3')
        self.assertEqual(test_class_4.name, 'test4')
