import importnb
import numpy as np
import sys
import pickle
import os
import inspect
import colorama
import unittest
import time
import textwrap
from unitgrade.runners import UTextResult
from unitgrade.utils import gprint, Capturing2, Capturing
colorama.init(autoreset=True)  # auto resets your settings after every output
import numpy
numpy.seterr(all='raise')

def setup_dir_by_class(C, base_dir):
    name = C.__class__.__name__
    return base_dir, name


class Report:
    title = "report title"
    abbreviate_questions = False # Should the test items start with 'Question ...' or just be q1).

    version = None
    questions = []
    pack_imports = []
    individual_imports = []
    nL = 120  # Maximum line width
    _config = None  # Private variable. Used when collecting results from student computers. Should only be read/written by teacher and never used for regular evaluation.

    @classmethod
    def reset(cls):
        for (q, _) in cls.questions:
            if hasattr(q, 'reset'):
                q.reset()

    @classmethod
    def mfile(clc):
        return inspect.getfile(clc)

    def _file(self):
        return inspect.getfile(type(self))

    def _import_base_relative(self):
        if hasattr(self.pack_imports[0], '__path__'):
            # im = self.pack_imports[0]
            # print("im!!!!")
            # print(im.__path__)
            # if isinstance(im, list):
            #     print("im is", im)
            # __path__ was originally not a list; but now it seems like it behaves like a list. Add check if problem persists and treat it as either list or string.
            # root_dir = self.pack_imports[0].__path__[0]._path[0]
            root_dir = self.pack_imports[0].__path__[0]

        else:
            root_dir = self.pack_imports[0].__file__

        root_dir = os.path.dirname(root_dir)
        relative_path = os.path.relpath(self._file(), root_dir)
        modules = os.path.normpath(relative_path[:-3]).split(os.sep)
        return root_dir, relative_path, modules

    def __init__(self, strict=False, payload=None):
        working_directory = os.path.abspath(os.path.dirname(self._file()))
        self.wdir, self.name = setup_dir_by_class(self, working_directory)
        # self.computed_answers_file = os.path.join(self.wdir, self.name + "_resources_do_not_hand_in.dat")
        for (q, _) in self.questions:
            q.nL = self.nL  # Set maximum line length.

        if payload is not None:
            self.set_payload(payload, strict=strict)

    def main(self, verbosity=1):
        # Run all tests using standard unittest (nothing fancy).
        loader = unittest.TestLoader()
        for q, _ in self.questions:
            start = time.time()  # A good proxy for setup time is to
            suite = loader.loadTestsFromTestCase(q)
            unittest.TextTestRunner(verbosity=verbosity).run(suite)
            total = time.time() - start
            q.time = total

    def _setup_answers(self, with_coverage=False):
        if with_coverage:
            for q, _ in self.questions:
                q._with_coverage = True
                q._report = self
        for q, _ in self.questions:
            q._setup_answers_mode = True

        from unitgrade import evaluate_report_student
        evaluate_report_student(self, unmute=True)

        # self.main()  # Run all tests in class just to get that out of the way...
        report_cache = {}
        for q, _ in self.questions:
            # print(self.questions)
            if hasattr(q, '_save_cache'):
                q()._save_cache()
                print("q is", q())
                # q()._cache_put('time', q.time) # = q.time
                report_cache[q.__qualname__] = q._cache2
            else:
                report_cache[q.__qualname__] = {'no cache see _setup_answers in framework.py': True}
        if with_coverage:
            for q, _ in self.questions:
                q._with_coverage = False
        return report_cache

    def set_payload(self, payloads, strict=False):
        for q, _ in self.questions:
            q._cache = payloads[q.__qualname__]
        self._config = payloads['config']


def get_hints(ss):
    if ss == None:
        return None
    try:
        ss = textwrap.dedent(ss)
        ss = ss.replace('''"""''', "").strip()
        hints = ["hints:", "hint:"]
        indexes = [ss.lower().find(h) for h in hints]
        j = np.argmax(indexes)
        if indexes[j] == -1:
            return None
        h = hints[j]
        ss = ss[ss.lower().find(h) + len(h) + 1:]
        ss = "\n".join([l for l in ss.split("\n") if not l.strip().startswith(":")])
        ss = textwrap.dedent(ss).strip()
        return ss
    except Exception as e:
        print("bad hints", ss, e)


class UTestCase(unittest.TestCase):
    _outcome = None  # A dictionary which stores the user-computed outcomes of all the tests. This differs from the cache.
    _cache = None  # Read-only cache. Ensures method always produce same result.
    _cache2 = None  # User-written cache.
    _with_coverage = False
    _covcache = None # Coverage cache. Written to if _with_coverage is true.
    _report = None  # The report used. This is very, very hacky and should always be None. Don't rely on it!

    # If true, the tests will not fail when cache is used. This is necesary since otherwise the cache will not be updated
    # during setup, and the deploy script must be run many times.
    _setup_answers_mode = False


    def capture(self):
        if hasattr(self, '_stdout') and self._stdout is not None:
            file = self._stdout
        else:
            # self._stdout = sys.stdout
            # sys._stdout = io.StringIO()
            file = sys.stdout
        return Capturing2(stdout=file)

    @classmethod
    def question_title(cls):
        """ Return the question title """
        if cls.__doc__ is not None:
            title = cls.__doc__.strip().splitlines()[0].strip()
            if not (title.startswith("Hints:") or title.startswith("Hint:") ):
                return title
        return cls.__qualname__

    @classmethod
    def reset(cls):
        print("Warning, I am not sure UTestCase.reset() is needed anymore and it seems very hacky.")
        cls._outcome = None
        cls._cache = None
        cls._cache2 = None

    def _callSetUp(self):
        if self._with_coverage:
            if self._covcache is None:
                self._covcache = {}
            import coverage
            self.cov = coverage.Coverage(data_file=None)
            self.cov.start()
        self.setUp()

    def _callTearDown(self):
        self.tearDown()
        # print("Teardown.")
        if self._with_coverage:
            # print("with cov")
            from pathlib import Path
            from snipper import snipper_main
            try:
                # print("Stoppping coverage...")
                self.cov.stop()
                # print("Coverage was stopped")
                # self.cov.html_report()
                # print("Success!")
            except Exception as e:
                print("Something went wrong while tearing down coverage test")
                print(e)
            data = self.cov.get_data()
            base, _, _ = self._report._import_base_relative()
            # print("Measured coverage files", data.measured_files)
            for file in data.measured_files():
                # print(file)
                file = os.path.normpath(file)
                root = Path(base)
                child = Path(file)
                # print("root", root, "child", child)
                # print(child, "is in parent?", root in child.parents)
                # print(child.parents)

                if root in child.parents:
                    # print("Reading file", child)
                    with open(child, 'r') as f:
                        s = f.read()
                    lines = s.splitlines()
                    garb = 'GARBAGE'
                    lines2 = snipper_main.censor_code(lines, keep=True)
                    # print("\n".join(lines2))
                    if len(lines) != len(lines2):
                        for k in range(len(lines)):
                            print(k, ">", lines[k], "::::::::", lines2[k])

                        # print("-" * 100)
                        # print("\n".join(lines))
                        # print("-"*100)
                        # print("\n".join(lines2))
                        # print("-" * 100)
                        print("Snipper failure; line lenghts do not agree. Exiting..")
                        print(child, "len(lines) == len(lines2)", len(lines), len(lines2))
                        import sys
                        sys.exit()

                    assert len(lines) == len(lines2)
                    # print("In file ", file, "context by lineno", data.contexts_by_lineno(file))
                    for ll in data.contexts_by_lineno(file):
                        # For empty files (e.g. __init__) there is a potential bug where coverage will return the file but lines2 will be = [].
                        # print("loop B: ll is", ll)
                        l = ll-1
                        # print(l)
                        # l1 = (lines[l] + " "*1000)[:80]
                        # l2 = (lines2[l] + " "*1000)[:80]
                        # print("l is", l, l1, " " + l2, "file", file)
                        # print("Checking if statement: ")
                        # print(l, lines2)
                        # print(">> ", lines2[l])
                        # print(">", lines2[l].strip(), garb)
                        if l < len(lines2) and lines2[l].strip() == garb:
                            # print("Got a hit at l", l)
                            rel = os.path.relpath(child, root)
                            cc = self._covcache
                            j = 0
                            for j in range(l, -1, -1):
                                if "def" in lines2[j] or "class" in lines2[j]:
                                    break
                            from snipper.legacy import gcoms
                            fun = lines2[j]
                            comments, _ = gcoms("\n".join(lines2[j:l]))
                            if rel not in cc:
                                cc[rel] = {}
                            cc[rel][fun] = (l, "\n".join(comments))
                            # print("found", rel, fun)
                            self._cache_put((self.cache_id(), 'coverage'), self._covcache)
        #                 print("ending loop B")
        #         print("At end of outer loop A")
        # print("-------------------------------------------- Tear down called")

    def shortDescriptionStandard(self):
        sd = super().shortDescription()
        if sd is None or sd.strip().startswith("Hints:") or sd.strip().startswith("Hint:"):
            sd = self._testMethodName
        return sd

    def shortDescription(self):
        sd = self.shortDescriptionStandard()
        title = self._cache_get((self.cache_id(), 'title'), sd)
        return title if title is not None else sd

    @property
    def title(self):
        return self.shortDescription()

    @title.setter
    def title(self, value):
        self._cache_put((self.cache_id(), 'title'), value)

    def _get_outcome(self):
        if not (self.__class__, '_outcome') or self.__class__._outcome is None:
            self.__class__._outcome = {}
        return self.__class__._outcome

    def _callTestMethod(self, testMethod):
        t = time.time()
        self._ensure_cache_exists()  # Make sure cache is there.
        if self._testMethodDoc is not None:
            self._cache_put((self.cache_id(), 'title'), self.shortDescriptionStandard())

        self._cache2[(self.cache_id(), 'assert')] = {}
        res = testMethod()
        elapsed = time.time() - t
        self._get_outcome()[ (self.cache_id(), "return") ] = res
        self._cache_put((self.cache_id(), "time"), elapsed)


    def cache_id(self):
        c = self.__class__.__qualname__
        m = self._testMethodName
        return c, m

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._load_cache()
        self._assert_cache_index = 0

    def _ensure_cache_exists(self):
        if not hasattr(self.__class__, '_cache') or self.__class__._cache == None:
            self.__class__._cache = dict()
        if not hasattr(self.__class__, '_cache2') or self.__class__._cache2 == None:
            self.__class__._cache2 = dict()

    def _cache_get(self, key, default=None):
        self._ensure_cache_exists()
        return self.__class__._cache.get(key, default)

    def _cache_put(self, key, value):
        self._ensure_cache_exists()
        self.__class__._cache2[key] = value

    def _cache_contains(self, key):
        self._ensure_cache_exists()
        return key in self.__class__._cache

    def wrap_assert(self, assert_fun, first, *args, **kwargs):
        key = (self.cache_id(), 'assert')
        if not self._cache_contains(key):
            print("Warning, framework missing", key)
            self.__class__._cache[
                key] = {}  # A new dict. We manually insert it because we have to use that the dict is mutable.
        cache = self._cache_get(key)
        id = self._assert_cache_index
        _expected = cache.get(id, f"Key {id} not found in cache; framework files missing. Please run deploy()")
        if not id in cache:
            print("Warning, framework missing cache index", key, "id =", id, " - The test will be skipped for now.")
            if self._setup_answers_mode:
                _expected = first # Bypass by setting equal to first. This is in case multiple self.assertEqualC's are run in a row and have to be set.

        # The order of these calls is important. If the method assert fails, we should still store the correct result in cache.
        cache[id] = first
        self._cache_put(key, cache)
        self._assert_cache_index += 1
        if not self._setup_answers_mode:
            assert_fun(first, _expected, *args, **kwargs)
        else:
            try:
                assert_fun(first, _expected, *args, **kwargs)
            except Exception as e:
                print("Mumble grumble. Cache function failed during class setup. Most likely due to old cache. Re-run deploy to check it pass.", id)
                print("> first", first)
                print("> expected", _expected)
                print(e)


    def assertEqualC(self, first, msg=None):
        self.wrap_assert(self.assertEqual, first, msg)

    def _shape_equal(self, first, second):
        a1 = np.asarray(first).squeeze()
        a2 = np.asarray(second).squeeze()
        msg = None
        msg = "" if msg is None else msg
        if len(msg) > 0:
            msg += "\n"
        self.assertEqual(a1.shape, a2.shape, msg=msg + "Dimensions of input data does not agree.")
        assert(np.all(np.isinf(a1) == np.isinf(a2)))  # Check infinite part.
        a1[np.isinf(a1)] = 0
        a2[np.isinf(a2)] = 0

        diff = np.abs(a1 - a2)

        # print(a1, a2, diff)
        return diff


    def assertLinf(self, first, second=None, tol=1e-5, msg=None):
        if second is None:
            return self.wrap_assert(self.assertLinf, first, tol=tol, msg=msg)
        else:
            diff = self._shape_equal(first, second)
            if max(diff.flat) >= tol:
                from unittest.util import safe_repr
                # msg = f'{safe_repr(first)} != {safe_repr(second)} : Not equal within tolerance {tol}'
                # print(msg)
                self.assertEqual(first, second, msg=f'Not equal within tolerance {tol}')

    def assertL2(self, first, second=None, tol=1e-5, msg=None):
        if second is None:
            return self.wrap_assert(self.assertL2, first, tol=tol, msg=msg)
        else:
            # We first test using numpys build-in testing method to see if one coordinate deviates a great deal.
            # This gives us better output, and we know that the coordinate wise difference is lower than the norm difference.
            np.testing.assert_allclose(first, second, atol=tol)
            diff = self._shape_equal(first, second)
            diff = ( ( np.asarray( diff.flatten() )**2).sum() )**.5
            if max(diff.flat) >= tol:
                self.assertEqual(first, second, msg=msg + f"Not equal within tolerance {tol}")

    def _cache_file(self):
        return os.path.dirname(inspect.getabsfile(type(self))) + "/unitgrade_data/" + self.__class__.__name__ + ".pkl"

    def _save_cache(self):
        # get the class name (i.e. what to save to).
        cfile = self._cache_file()
        if not os.path.isdir(os.path.dirname(cfile)):
            os.makedirs(os.path.dirname(cfile))

        if hasattr(self.__class__, '_cache2'):
            with open(cfile, 'wb') as f:
                pickle.dump(self.__class__._cache2, f)

    # But you can also set cache explicitly.
    def _load_cache(self):
        if self._cache is not None:  # Cache already loaded. We will not load it twice.
            return
            # raise Exception("Loaded cache which was already set. What is going on?!")
        cfile = self._cache_file()
        if os.path.exists(cfile):
            try:
                # print("\ncache file", cfile)
                with open(cfile, 'rb') as f:
                    data = pickle.load(f)
                self.__class__._cache = data
            except Exception as e:
                print("Bad cache", cfile)
                print(e)
        else:
            print("Warning! data file not found", cfile)

    # def _feedFailuresToResult(self, result, errors):
    #     print("asdfdf")

    def _feedErrorsToResult(self, result, errors):
        """ Use this to show hints on test failure. """
        if not isinstance(result, UTextResult):
            er = [e for e, v in errors if v != None]
            # print("Errors are", errors)
            if len(er) > 0:
                hints = []
                key = (self.cache_id(), 'coverage')
                if self._cache_contains(key):
                    CC = self._cache_get(key)
                    cl, m = self.cache_id()
                    gprint(f"> An error occured while solving: {cl}.{m}. The files/methods you need to edit are:")  # For the test {id} in {file} you should edit:")
                    for file in CC:
                        rec = CC[file]
                        gprint(f">   * {file}")
                        for l in rec:
                            _, comments = CC[file][l]
                            hint = get_hints(comments)

                            if hint != None:
                                hints.append((hint, file, l) )
                            gprint(f">      - {l}")

                er = er[0]
                doc = er._testMethodDoc
                # print("doc", doc)
                if doc is not None:
                    hint = get_hints(er._testMethodDoc)
                    if hint is not None:
                        hints = [(hint, None, self.cache_id()[1] )] + hints
                if len(hints) > 0:
                    # print(hints)
                    for hint, file, method in hints:
                        s = (f"'{method.strip()}'" if method is not None else "")
                        if method is not None and file is not None:
                            s += " in "
                        try:
                            s += (file.strip() if file is not None else "")
                            gprint(">")
                            gprint("> Hints (from " + s + ")")
                            gprint(textwrap.indent(hint, ">   "))
                        except Exception as e:
                            print("Bad stuff in hints. ")
                            print(hints)

        super()._feedErrorsToResult(result, errors)

    def startTestRun(self):
        super().startTestRun()

# 817, 705
class NotebookTestCase(UTestCase):
    notebook = None
    _nb = None
    @classmethod
    def setUpClass(cls) -> None:
        with Capturing():
            cls._nb = importnb.Notebook.load(cls.notebook)

    @property
    def nb(self):
        return self.__class__._nb