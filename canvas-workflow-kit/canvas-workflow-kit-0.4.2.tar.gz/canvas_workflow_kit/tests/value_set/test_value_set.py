from unittest import TestCase
from canvas_workflow_kit.value_set.value_set import *


class SuperValueSetTest(TestCase):
    class ValSetA(ValueSet):
        OID = '1.2.3.4'
        VALUE_SET_NAME = 'Set A'
        CPT = {'A_abc', 'A_123'}
        SNOMEDCT = {'A_12345', 'A_23456', 'A_34567'}

    class ValSetB(ValueSet):
        OID = '2.3.4'
        VALUE_SET_NAME = 'Set B'
        CPT = {'B_abc', 'B_123'}
        ICD10CM = {'B_12345', 'B_23456', 'B_34567'}

    class ValSetC(ValueSet):
        OID = '2.5.6'
        VALUE_SET_NAME = 'Set B'
        CPT = {'C_abc', 'C_123'}
        ICD10CM = {'C_12345', 'C_23456', 'C_34567'}

    def test_def(self):
        value_sets = [self.ValSetA, self.ValSetB]
        result = SuperValueSet(value_sets)

        self.assertEqual(len(value_sets), len(result.value_sets))
        if not (result.value_sets[0] is self.ValSetA):
            self.assertIs(self.ValSetB, result.value_sets[0])
        if not (result.value_sets[1] is self.ValSetA):
            self.assertIs(self.ValSetB, result.value_sets[1])

    def test_values(self):
        value_sets = [self.ValSetA, self.ValSetB]
        result = SuperValueSet(value_sets)

        self.assertIsInstance(result.values, defaultdict)
        result = result.values

        expected = {
            'cpt': {'B_123', 'A_123', 'A_abc', 'B_abc'},
            'snomedct': {'A_12345', 'A_34567', 'A_23456'},
            'icd10cm': {'B_12345', 'B_34567', 'B_23456'}
        }
        self.assertEqual(len(expected), len(result))
        for key, val in expected.items():
            self.assertTrue(key in result)
            self.assertEqual(sorted(list(val)), sorted(list(result[key])))

    def test_name(self):
        value_sets = [self.ValSetA, self.ValSetB]
        result = SuperValueSet(value_sets)
        expected = 'Set A or Set B'
        self.assertEqual(expected, result.name)

    def test___or__(self):
        value_sets = [self.ValSetA, self.ValSetB]
        sup_ab = SuperValueSet(value_sets)
        value_sets = [self.ValSetC, self.ValSetB]
        sup_cb = SuperValueSet(value_sets)

        result = sup_ab | sup_cb
        self.assertIsInstance(result, SuperValueSet)

        expected = {
            'cpt': {'C_123', 'B_abc', 'C_abc', 'B_123', 'A_123', 'A_abc'},
            'snomedct': {'A_23456', 'A_34567', 'A_12345'},
            'icd10cm': {'B_34567', 'C_23456', 'C_12345', 'B_23456', 'C_34567', 'B_12345'}
        }
        result = result.values
        self.assertEqual(len(expected), len(result))
        for key, val in expected.items():
            self.assertTrue(key in result)
            self.assertEqual(sorted(list(val)), sorted(list(result[key])))


class ValueSystemsTest(TestCase):

    def test_values(self):
        # all systems + one unknown
        class FullValSet(ValueSet):
            OID = '1.2.3.4'
            VALUE_SET_NAME = 'Reco for the unit tests'
            CPT = {'A_abc', 'A_123'}
            CVX = {'B_12345', 'B_23456', 'B_34567'}
            HCPCS = {'C_abc', 'C_123'}
            ICD10CM = {'D_12345', 'D_23456', 'D_34567'}
            ICD10PCS = {'E_abc', 'E_123'}
            ICD9CM = {'F_12345', 'F_23456', 'F_34567'}
            LOINC = {'G_abc', 'G_123'}
            RXNORM = {'H_12345', 'H_23456', 'H_34567'}
            SNOMEDCT = {'I_12345', 'I_23456', 'I_34567'}
            ZZZZZ = {'K_12345', 'K_23456', 'K_34567'}

        expected = {
            'cpt': {'A_123', 'A_abc'},
            'cvx': {'B_34567', 'B_23456', 'B_12345'},
            'hcpcs': {'C_123', 'C_abc'},
            'icd10cm': {'D_34567', 'D_12345', 'D_23456'},
            'icd10pcs': {'E_123', 'E_abc'},
            'icd9cm': {'F_12345', 'F_34567', 'F_23456'},
            'loinc': {'G_abc', 'G_123'},
            'rxnorm': {'H_12345', 'H_23456', 'H_34567'},
            'snomedct': {'I_34567', 'I_12345', 'I_23456'}
        }
        result = FullValSet.values
        self.assertEqual(len(expected), len(result))
        for key, val in expected.items():
            tmp = False
            if key in result:
                self.assertEqual(sorted(list(val)), sorted(list(result[key])))
                tmp = True
            self.assertTrue(tmp)

        # only 2 systems
        class PartValSet(ValueSet):
            OID = '1.2.3.4'
            VALUE_SET_NAME = 'Reco for the unit tests'
            CPT = {'A_abc', 'A_123'}
            SNOMEDCT = {'I_12345', 'I_23456', 'I_34567'}
            ZZZZZ = {'K_12345', 'K_23456', 'K_34567'}

        expected = {
            'cpt': {'A_123', 'A_abc'},
            'snomedct': {'I_34567', 'I_12345', 'I_23456'}
        }
        result = PartValSet.values
        self.assertEqual(len(expected), len(result))
        for key, val in expected.items():
            tmp = False
            if key in result:
                self.assertEqual(sorted(list(val)), sorted(list(result[key])))
                tmp = True
            self.assertTrue(tmp)

        # no system
        class PartValSet(ValueSet):
            OID = '1.2.3.4'
            VALUE_SET_NAME = 'Reco for the unit tests'
            ZZZZZ = {'K_12345', 'K_23456', 'K_34567'}

        expected = {}
        result = PartValSet.values
        self.assertEqual(len(expected), len(result))

    def test_name(self):
        class PartValSet(ValueSet):
            OID = '1.2.3.4'
            VALUE_SET_NAME = 'Reco for the unit tests'
            ZZZZZ = {'K_12345', 'K_23456', 'K_34567'}

        expected = 'Reco for the unit tests'
        result = PartValSet.name
        self.assertEqual(expected, result)

    def test___or__(self):
        class ValSetA(ValueSet):
            OID = '1.2.3.4'
            VALUE_SET_NAME = 'Set A'
            CPT = {'A_abc', 'A_123'}
            SNOMEDCT = {'A_12345', 'A_23456', 'A_34567'}

        class ValSetB(ValueSet):
            OID = '2.3.4'
            VALUE_SET_NAME = 'Set B'
            CPT = {'B_abc', 'B_123'}
            ICD10CM = {'B_12345', 'B_23456', 'B_34567'}

        expected = {
            'cpt': {'B_123', 'A_123', 'B_abc', 'A_abc'},
            'snomedct': {'A_34567', 'A_23456', 'A_12345'},
            'icd10cm': {'B_34567', 'B_23456', 'B_12345'}
        }
        result = ValSetA | ValSetB
        self.assertIsInstance(result, SuperValueSet)

        result = result.values
        self.assertEqual(len(expected), len(result))
        for key, val in expected.items():
            self.assertTrue(key in result)
            self.assertEqual(sorted(list(val)), sorted(list(result[key])))


class ValueSetTest(TestCase):

    def test_value_system(self):
        class UnitTestReco(ValueSet):
            OID = '1.2.3.4'
            VALUE_SET_NAME = 'Reco for the unit tests'
            CPT = {'abc', '123'}
            SNOMEDCT = {'12345', '23456', '34567'}

        rec = UnitTestReco()
        expected = ['CANVAS', 'CPT', 'CVX', 'HCPCS', 'ICD10CM', 'ICD10PCS', 'ICD9CM', 'LOINC', 'RXNORM', 'SNOMEDCT', 'FDB', 'INTERNAL', ]
        result = rec.value_systems
        self.assertEqual(expected, result)
