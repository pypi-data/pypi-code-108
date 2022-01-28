import hashlib
import io
import tokenize
import numpy as np
from tabulate import tabulate
from datetime import datetime
import pyfiglet
from unitgrade import msum
import unittest
from unitgrade.runners import UTextResult, UTextTestRunner
import inspect
import os
import argparse
import time

parser = argparse.ArgumentParser(description='Evaluate your report.', epilog="""Example: 
To run all tests in a report: 

> python assignment1_dp.py

To run only question 2 or question 2.1

> python assignment1_dp.py -q 2
> python assignment1_dp.py -q 2.1

Note this scripts does not grade your report. To grade your report, use:

> python report1_grade.py

Finally, note that if your report is part of a module (package), and the report script requires part of that package, the -m option for python may be useful.
For instance, if the report file is in Documents/course_package/report3_complete.py, and `course_package` is a python package, then change directory to 'Documents/` and run:

> python -m course_package.report1

see https://docs.python.org/3.9/using/cmdline.html
""", formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-q', nargs='?', type=str, default=None, help='Only evaluate this question (e.g.: -q 2)')
parser.add_argument('--showexpected',  action="store_true",  help='Show the expected/desired result')
parser.add_argument('--showcomputed',  action="store_true",  help='Show the answer your code computes')
parser.add_argument('--unmute',  action="store_true",  help='Show result of print(...) commands in code')
parser.add_argument('--passall',  action="store_true",  help='Automatically pass all tests. Useful when debugging.')
parser.add_argument('--noprogress',  action="store_true",  help='Disable progress bars.')

def evaluate_report_student(report, question=None, qitem=None, unmute=None, passall=None, ignore_missing_file=False, show_tol_err=False, show_privisional=True, noprogress=None):
    args = parser.parse_args()
    if noprogress is None:
        noprogress = args.noprogress

    if question is None and args.q is not None:
        question = args.q
        if "." in question:
            question, qitem = [int(v) for v in question.split(".")]
        else:
            question = int(question)

    if hasattr(report, "computed_answer_file") and not os.path.isfile(report.computed_answers_file) and not ignore_missing_file:
        raise Exception("> Error: The pre-computed answer file", os.path.abspath(report.computed_answers_file), "does not exist. Check your package installation")

    if unmute is None:
        unmute = args.unmute
    if passall is None:
        passall = args.passall

    results, table_data = evaluate_report(report, question=question, show_progress_bar=not unmute and not noprogress, qitem=qitem,
                                          verbose=False, passall=passall, show_expected=args.showexpected, show_computed=args.showcomputed,unmute=unmute,
                                          show_tol_err=show_tol_err)


    if question is None and show_privisional:
        print("Provisional evaluation")
        tabulate(table_data)
        table = table_data
        print(tabulate(table))
        print(" ")

    fr = inspect.getouterframes(inspect.currentframe())[1].filename
    gfile = os.path.basename(fr)[:-3] + "_grade.py"
    if os.path.exists(gfile):
        print("Note your results have not yet been registered. \nTo register your results, please run the file:")
        print(">>>", gfile)
        print("In the same manner as you ran this file.")


    return results


def upack(q):
    # h = zip([(i['w'], i['possible'], i['obtained']) for i in q.values()])
    h =[(i['w'], i['possible'], i['obtained']) for i in q.values()]
    h = np.asarray(h)
    return h[:,0], h[:,1], h[:,2],

# class UnitgradeTextRunner(unittest.TextTestRunner):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

class SequentialTestLoader(unittest.TestLoader):
    def getTestCaseNames(self, testCaseClass):
        test_names = super().getTestCaseNames(testCaseClass)
        # testcase_methods = list(testCaseClass.__dict__.keys())
        ls = []
        for C in testCaseClass.mro():
            if issubclass(C, unittest.TestCase):
                ls = list(C.__dict__.keys()) + ls
        testcase_methods = ls
        test_names.sort(key=testcase_methods.index)
        return test_names

def evaluate_report(report, question=None, qitem=None, passall=False, verbose=False,  show_expected=False, show_computed=False,unmute=False, show_help_flag=True, silent=False,
                    show_progress_bar=True,
                    show_tol_err=False,
                    big_header=True):

    from unitgrade.version import __version__
    now = datetime.now()
    if big_header:
        ascii_banner = pyfiglet.figlet_format("UnitGrade", font="doom")
        b = "\n".join( [l for l in ascii_banner.splitlines() if len(l.strip()) > 0] )
    else:
        b = "Unitgrade"
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print(b + " v" + __version__ + ", started: " + dt_string+ "\n")
    # print("Started: " + dt_string)
    s = report.title
    if hasattr(report, "version") and report.version is not None:
        s += " version " + report.version
    print(s, "(use --help for options)" if show_help_flag else "")
    # print(f"Loaded answers from: ", report.computed_answers_file, "\n")
    table_data = []
    t_start = time.time()
    score = {}
    loader = SequentialTestLoader()

    for n, (q, w) in enumerate(report.questions):
        if question is not None and n+1 != question:
            continue
        suite = loader.loadTestsFromTestCase(q)
        qtitle = q.question_title() if hasattr(q, 'question_title') else q.__qualname__
        if not report.abbreviate_questions:
            q_title_print = "Question %i: %s"%(n+1, qtitle)
        else:
            q_title_print = "q%i) %s" % (n + 1, qtitle)

        print(q_title_print, end="")
        q.possible = 0
        q.obtained = 0
        # q_ = {} # Gather score in this class.
        UTextResult.q_title_print = q_title_print # Hacky
        UTextResult.show_progress_bar = show_progress_bar # Hacky.
        UTextResult.number = n
        UTextResult.nL = report.nL
        UTextResult.unmute = unmute # Hacky as well.
        UTextResult.setUpClass_time = q._cache.get(((q.__name__, 'setUpClass'), 'time'), 3) if hasattr(q, '_cache') and q._cache is not None else 3


        res = UTextTestRunner(verbosity=2, resultclass=UTextResult).run(suite)
        details = {}
        for s, msg in res.successes + res.failures + res.errors:
            # from unittest.suite import _ErrorHolder
            # from unittest import _Err
            # if isinstance(s, _ErrorHolder)
            if hasattr(s, '_testMethodName'):
                key = (q.__name__, s._testMethodName)
            else:
                # In case s is an _ErrorHolder (unittest.suite)
                key = (q.__name__, s.id())
            # key = (q.__name__, s._testMethodName) # cannot use the cache_id method bc. it is not compatible with plain unittest.

            detail = {}
            if (s,msg) in res.successes:
                detail['status'] = "pass"
            elif (s,msg) in res.failures:
                detail['status'] = 'fail'
            elif (s,msg) in res.errors:
                detail['status'] = 'error'
            else:
                raise Exception("Status not known.")
            detail = {**detail, **msg}#['message'] = msg
            details[key] = detail

        # q_[s._testMethodName] = ("pass", None)
        # for (s,msg) in res.failures:
        #     q_[s._testMethodName] = ("fail", msg)
        # for (s,msg) in res.errors:
        #     q_[s._testMethodName] = ("error", msg)
        # res.successes[0]._get_outcome()

        possible = res.testsRun
        obtained = len(res.successes)

        # assert len(res.successes) +  len(res.errors) + len(res.failures) == res.testsRun

        obtained = int(w * obtained * 1.0 / possible ) if possible > 0 else 0
        score[n] = {'w': w, 'possible': w, 'obtained': obtained, 'items': details, 'title': qtitle, 'name': q.__name__,
                   }
        q.obtained = obtained
        q.possible = possible
        # print(q._cache)
        # print(q._covcache)
        s1 = f" * q{n+1})   Total"
        s2 = f" {q.obtained}/{w}"
        print(s1 + ("."* (report.nL-len(s1)-len(s2) )) + s2 )
        print(" ")
        table_data.append([f"q{n+1}) Total", f"{q.obtained}/{w}"])

    ws, possible, obtained = upack(score)
    possible = int( msum(possible) )
    obtained = int( msum(obtained) ) # Cast to python int
    report.possible = possible
    report.obtained = obtained
    now = datetime.now()
    dt_string = now.strftime("%H:%M:%S")

    dt = int(time.time()-t_start)
    minutes = dt//60
    seconds = dt - minutes*60
    plrl = lambda i, s: str(i) + " " + s + ("s" if i != 1 else "")

    from unitgrade.utils import dprint
    dprint(first = "Total points at "+ dt_string + " (" + plrl(minutes, "minute") + ", "+ plrl(seconds, "second") +")",
           last=""+str(report.obtained)+"/"+str(report.possible), nL = report.nL)

    # print(f"Completed at "+ dt_string + " (" + plrl(minutes, "minute") + ", "+ plrl(seconds, "second") +"). Total")

    table_data.append(["Total", ""+str(report.obtained)+"/"+str(report.possible) ])
    results = {'total': (obtained, possible), 'details': score}
    return results, table_data


def python_code_str_id(python_code, strip_comments_and_docstring=True):
    s = python_code
    if strip_comments_and_docstring:
        s = remove_comments_and_docstrings(s)
    s = "".join([c.strip() for c in s.split()])
    hash_object = hashlib.blake2b(s.encode())
    return hash_object.hexdigest()


def file_id(file, strip_comments_and_docstring=True):
    with open(file, 'r') as f:
        # s = f.read()
        return python_code_str_id(f.read())


def remove_comments_and_docstrings(source):
    """
    Returns 'source' minus comments and docstrings.
    """
    io_obj = io.StringIO(source)
    out = ""
    prev_toktype = tokenize.INDENT
    last_lineno = -1
    last_col = 0
    for tok in tokenize.generate_tokens(io_obj.readline):
        token_type = tok[0]
        token_string = tok[1]
        start_line, start_col = tok[2]
        end_line, end_col = tok[3]
        ltext = tok[4]
        # The following two conditionals preserve indentation.
        # This is necessary because we're not using tokenize.untokenize()
        # (because it spits out code with copious amounts of oddly-placed
        # whitespace).
        if start_line > last_lineno:
            last_col = 0
        if start_col > last_col:
            out += (" " * (start_col - last_col))
        # Remove comments:
        if token_type == tokenize.COMMENT:
            pass
        # This series of conditionals removes docstrings:
        elif token_type == tokenize.STRING:
            if prev_toktype != tokenize.INDENT:
        # This is likely a docstring; double-check we're not inside an operator:
                if prev_toktype != tokenize.NEWLINE:
                    # Note regarding NEWLINE vs NL: The tokenize module
                    # differentiates between newlines that start a new statement
                    # and newlines inside of operators such as parens, brackes,
                    # and curly braces.  Newlines inside of operators are
                    # NEWLINE and newlines that start new code are NL.
                    # Catch whole-module docstrings:
                    if start_col > 0:
                        # Unlabelled indentation means we're inside an operator
                        out += token_string
                    # Note regarding the INDENT token: The tokenize module does
                    # not label indentation inside of an operator (parens,
                    # brackets, and curly braces) as actual indentation.
                    # For example:
                    # def foo():
                    #     "The spaces before this docstring are tokenize.INDENT"
                    #     test = [
                    #         "The spaces before this string do not get a token"
                    #     ]
        else:
            out += token_string
        prev_toktype = token_type
        last_col = end_col
        last_lineno = end_line
    return out