import unittest
from pyfaust.tests.TestFaust import TestFaust
from pyfaust.tests.TestPoly import TestPoly
import sys

dev = 'cpu'
field = 'real'

if __name__ == "__main__":
    nargs = len(sys.argv)
    if(nargs > 1):
        dev = sys.argv[1]
        if dev != 'cpu' and not dev.startswith('gpu'):
            raise ValueError("dev argument must be cpu or gpu.")
        if(nargs > 2):
            field = sys.argv[2]
            if field not in ['complex', 'real']:
                raise ValueError("field must be complex or float")
        del sys.argv[2]  # deleted to avoid interfering with unittest
        del sys.argv[1]
    if(nargs > 1):
        # it remains a method fully qualified method name to test
        # e.g. TestFaust.test_transpose
        class_name, meth_name = sys.argv[1].split('.')[:]
        testloader = unittest.TestLoader()
        test_names = eval("testloader.getTestCaseNames("+class_name+")")
        if meth_name in test_names:
            test = eval(""+class_name+"('"+meth_name+"', dev=dev, field=field)")
        else:
            raise ValueError(meth_name +" is not in "+class_name)
        suite = unittest.TestSuite()
        suite.addTest(test)
        runner = unittest.TextTestRunner()
        runner.run(suite)
    else:
        # run all tests
        unittest.main()
