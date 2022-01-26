"""
pip install pureyaml
python -c "
import unittest, pureyaml
print(pureyaml.dump(sorted([e for e in dir(unittest.TestCase) if not e.startswith('_')])))
"
- addCleanup
- addTypeEqualityFunc
- assertAlmostEqual
- assertAlmostEquals
- assertDictContainsSubset
- assertDictEqual
- assertEqual
- assertEquals
- assertFalse
- assertGreater
- assertGreaterEqual
- assertIn
- assertIs
- assertIsInstance
- assertIsNone
- assertIsNot
- assertIsNotNone
- assertItemsEqual
- assertLess
- assertLessEqual
- assertListEqual
- assertMultiLineEqual
- assertNotAlmostEqual
- assertNotAlmostEquals
- assertNotEqual
- assertNotEquals
- assertNotIn
- assertNotIsInstance
- assertNotRegexpMatches
- assertRaises
- assertRaisesRegexp
- assertRegexpMatches
- assertSequenceEqual
- assertSetEqual
- assertTrue
- assertTupleEqual
- assert_
- countTestCases
- debug
- defaultTestResult
- doCleanups
- fail
- failIf
- failIfAlmostEqual
- failIfEqual
- failUnless
- failUnlessAlmostEqual
- failUnlessEqual
- failUnlessRaises
- failureException
- id
- longMessage
- maxDiff
- run
- setUp
- setUpClass
- shortDescription
- skipTest
- tearDown
- tearDownClass

"""