import io
import sys
import time
import unittest
from unittest.runner import _WritelnDecorator
import numpy as np
from unitgrade import ActiveProgress


class UTextResult(unittest.TextTestResult):
    nL = 80
    number = -1  # HAcky way to set question number.
    show_progress_bar = True
    unmute = False # Whether to redirect stdout.
    cc = None
    setUpClass_time = 3 # Estimated time to run setUpClass in TestCase. Must be set externally. See key (("ClassName", "setUpClass"), "time") in _cache.

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.successes = []

    def printErrors(self) -> None:
        # TODO: Fix here. probably also needs to flush stdout.
        self.printErrorList('ERROR', [(test, res['stderr']) for test, res in self.errors])
        self.printErrorList('FAIL',  [(test, res['stderr']) for test, res in self.failures])

    def addError(self, test, err):
        super(unittest.TextTestResult, self).addError(test, err)
        err = self.errors[-1][1]
        if hasattr(sys.stdout, 'log'):
            stdout = sys.stdout.log.readlines()  # Only works because we set sys.stdout to a unitgrade.Logger
        else:
            stdout = ""
        self.errors[-1] = (self.errors[-1][0], {'return': None,
                                'stderr': err,
                                'stdout': stdout
                                })

        if not hasattr(self, 'item_title_print'):
            # In case setUpClass() fails with an error the short description may not be set. This will fix that problem.
            self.item_title_print = test.shortDescription()
            if self.item_title_print is None:  # In case the short description is not set either...
                self.item_title_print = test.id()


        self.cc_terminate(success=False)

    def addFailure(self, test, err):
        super(unittest.TextTestResult, self).addFailure(test, err)
        err = self.failures[-1][1]
        stdout = sys.stdout.log.readlines()  # Only works because we set sys.stdout to a unitgrade.Logger
        self.failures[-1] = (self.failures[-1][0], {'return': None,
                                'stderr': err,
                                'stdout': stdout
                                })
        self.cc_terminate(success=False)


    def addSuccess(self, test: unittest.case.TestCase) -> None:
        msg = None
        stdout = sys.stdout.log.readlines() # Only works because we set sys.stdout to a unitgrade.Logger

        if hasattr(test, '_get_outcome'):
            o = test._get_outcome()
            if isinstance(o, dict):
                key = (test.cache_id(), "return")
                if key in o:
                    msg = test._get_outcome()[key]

        # print(sys.stdout.readlines())
        self.successes.append((test, None))  # (test, message) (to be consistent with failures and errors).
        self.successes[-1] = (self.successes[-1][0], {'return': msg,
                                 'stdout': stdout,
                                 'stderr': None})

        self.cc_terminate()

    def cc_terminate(self, success=True):
        if self.show_progress_bar or True:
            tsecs = np.round(self.cc.terminate(), 2)
            self.cc.file.flush()
            ss = self.item_title_print

            state = "PASS" if success else "FAILED"

            dot_parts = ('.' * max(0, self.nL - len(state) - len(ss)))
            if self.show_progress_bar or True:
                print(self.item_title_print + dot_parts, end="", file=self.cc.file)
            else:
                print(dot_parts, end="", file=self.cc.file)

            if tsecs >= 0.5:
                state += " (" + str(tsecs) + " seconds)"
            print(state, file=self.cc.file)

    def startTest(self, test):
        name = test.__class__.__name__
        if self.testsRun == 0 and hasattr(test.__class__, '_cache2'): # Disable this if the class is pure unittest.TestCase
            # This is the first time we are running a test. i.e. we can time the time taken to call setupClass.
            if test.__class__._cache2 is None:
                test.__class__._cache2 = {}
            test.__class__._cache2[((name, 'setUpClass'), 'time')] = time.time() - self.t_start

        self.testsRun += 1
        item_title = test.shortDescription()  # Better for printing (get from cache).

        if item_title == None:
            # For unittest framework where getDescription may return None.
            item_title = self.getDescription(test)
        self.item_title_print = " * q%i.%i) %s" % (UTextResult.number + 1, self.testsRun, item_title)
        if self.show_progress_bar or True:
            estimated_time = test.__class__._cache.get(((name, test._testMethodName), 'time'), 100) if hasattr(test.__class__, '_cache') else 4
            self.cc = ActiveProgress(t=estimated_time, title=self.item_title_print, show_progress_bar=self.show_progress_bar, file=sys.stdout)
        else:
            print(self.item_title_print + ('.' * max(0, self.nL - 4 - len(self.item_title_print))), end="")
        self._test = test

        # if not self.unmute:
        self._stdout = sys.stdout # Redundant. remove later.
        from unitgrade.utils import Logger
        sys.stdout = Logger(io.StringIO(), write_to_stdout=self.unmute)

    def stopTest(self, test):
        # if not self.unmute:
        buff = sys.stdout.log
        sys.stdout = self._stdout # redundant.
        buff.close()

        from unitgrade.utils import Logger

        super().stopTest(test)

    def _setupStdout(self):
        if self._previousTestClass == None:
            self.t_start = time.time()
            if hasattr(self.__class__, 'q_title_print'):
                q_title_print = self.__class__.q_title_print
            else:
                q_title_print = "<unnamed test. See unitgrade.framework.py>"

            cc = ActiveProgress(t=self.setUpClass_time, title=q_title_print, show_progress_bar=self.show_progress_bar)
            self.cc = cc

    def _restoreStdout(self):  # Used when setting up the test.
        if self._previousTestClass is None:
            q_time = self.cc.terminate()
            q_time = np.round(q_time, 2)
            sys.stdout.flush()
            if self.show_progress_bar:
                print(self.cc.title, end="")
            print(" " * max(0, self.nL - len(self.cc.title)) + (" (" + str(q_time) + " seconds)" if q_time >= 0.5 else ""))


class UTextTestRunner(unittest.TextTestRunner):
    def __init__(self, *args, **kwargs):
        stream = io.StringIO()
        super().__init__(*args, stream=stream, **kwargs)

    def _makeResult(self):
        # stream = self.stream # not you!
        stream = sys.stdout
        stream = _WritelnDecorator(stream)
        return self.resultclass(stream, self.descriptions, self.verbosity)