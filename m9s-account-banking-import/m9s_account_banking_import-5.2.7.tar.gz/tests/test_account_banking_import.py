# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import unittest

from trytond.tests.test_tryton import ModuleTestCase
from trytond.tests.test_tryton import suite as test_suite


class AccountBankingImportTestCase(ModuleTestCase):
    'Test Account Banking Import module'
    module = 'account_banking_import'


def suite():
    suite = test_suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            AccountBankingImportTestCase))
    return suite
