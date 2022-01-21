# -*- coding: utf-8 -*-
#
# system utilities methods
# IMIO <support@imio.be>
#

from imio.pyutils.utils import replace_in_list

import types
import unittest


class TestUtils(unittest.TestCase):
    """ """

    def test_replace_in_list(self):
        self.assertEqual(replace_in_list([1, 2, 3], 1, 4), [4, 2, 3])
        self.assertEqual(replace_in_list([1, 2, 3], 4, 5), [1, 2, 3])
        self.assertEqual(replace_in_list([1, 2, 3, 1], 1, 5), [5, 2, 3, 5])
        # generator
        res = replace_in_list([1, 2, 3], 1, 4, generator=True)
        self.assertTrue(isinstance(res, types.GeneratorType))
        self.assertEqual(list(res), [4, 2, 3])
