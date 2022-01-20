# -*- coding: utf-8 -*-
"""test runner."""
import ast
import logging
import os
import pathlib
import re
import shutil
import sys
from typing import Dict

import junit_xml

from yea import testspec, ytest

from .yeadoc import YeadocSnippet, load_tests_from_docstring


logger = logging.getLogger(__name__)


def convert(text):
    return int(text) if text.isdigit() else text.lower()


def alphanum_sort(key):
    return [convert(c) for c in re.split("([0-9]+)", key._sort_key)]


class TestRunner:
    def __init__(self, *, yc):
        self.prepare()
        self._yc = yc
        self._cfg = yc._cfg
        self._args = yc._args
        self._test_files = []
        self._results = []
        self._test_list = []
        self._populate()

    def prepare(self):
        # initialize
        self._tmpdir = pathlib.Path.cwd() / ".yeadoc"
        if self._tmpdir.exists():
            shutil.rmtree(self._tmpdir)
        self._tmpdir.mkdir()

    def clean(self):
        if self._tmpdir.exists():
            shutil.rmtree(self._tmpdir)

    def _get_args_list(self):
        # TODO: clean up args parsing
        args_tests = getattr(self._args, "tests", None)
        if not args_tests:
            return None

        alist = []
        for a in args_tests:
            p = pathlib.Path(a)
            p = p.resolve()
            alist.append(str(p))
        return alist

    def _get_dirs(self):
        # generate to return all test dirs and recursively found dirs
        for tdir in self._cfg.test_dirs:
            path_dir = pathlib.Path(self._cfg.test_root, tdir)
            yield path_dir
            for root, dirs, _ in os.walk(path_dir, topdown=True):
                # TODO: temporary hack to avoid walking into wandb dir
                # use .gitignore instead
                if "wandb" in dirs:
                    dirs.remove("wandb")
                if ".tox" in dirs:
                    dirs.remove(".tox")
                for d in dirs:
                    path_dir = pathlib.Path(self._cfg.test_root, root, d)
                    yield path_dir

    def _populate(self):
        tpaths = []

        args_tests = self._get_args_list() or []

        all_tests = False
        if self._args.action == "list" and not self._args.tests:
            all_tests = True
        if self._args.action == "run" and self._args.all:
            all_tests = True

        if not self._args.docs_only:
            for path_dir in self._get_dirs():
                # TODO: look for .yea, or look for .py with docstring
                for tpath in path_dir.glob("*.py"):
                    if not all_tests and str(tpath) not in args_tests:
                        logger.debug("skip fname {}".format(tpath))
                        continue
                    docstr = testspec.load_docstring(tpath)
                    spec = testspec.load_yaml_from_docstring(docstr)
                    if not spec:
                        logger.debug("skip nospec {}".format(tpath))
                        continue

                    if all_tests:
                        if spec.get("tag", {}).get("skip", False):
                            continue
                        suite = spec.get("tag", {}).get("suite", "main")
                        shard = spec.get("tag", {}).get("shard", "default")
                        if self._args.suite and self._args.suite != suite:
                            continue
                        if self._args.shard and self._args.shard != shard:
                            continue

                    tpaths.append(tpath)
                for tpath in path_dir.glob("*.yea"):
                    # TODO: parse yea file looking for path info
                    spec = testspec.load_yaml_from_file(tpath)

                    # if program is specified, keep track of yea file
                    py_fname = spec.get("command", {}).get("program")
                    if py_fname:
                        # hydrate to full path, take base from tpath
                        py_fname = os.path.join(tpath.parent, py_fname)
                        t_fname = tpath
                    else:
                        py_fname = str(tpath)[:-4] + ".py"
                        t_fname = py_fname

                    if not os.path.exists(py_fname):
                        continue

                    # TODO: DRY. code is same as above, refactor sometime
                    if all_tests:
                        if spec.get("tag", {}).get("skip", False):
                            continue
                        suite = spec.get("tag", {}).get("suite", "main")
                        shard = spec.get("tag", {}).get("shard", "default")
                        if self._args.suite and self._args.suite != suite:
                            continue
                        if self._args.shard and self._args.shard != shard:
                            continue

                    if not all_tests:
                        if py_fname not in args_tests and str(tpath) not in args_tests:
                            logger.debug("skip yea fname {}".format(tpath))
                            continue

                    # add .yea or .py file
                    tpaths.append(pathlib.Path(t_fname))

        # pick up yea tests from docstrings
        id_test_map: Dict[str, YeadocSnippet] = {}
        for path_dir in self._get_dirs():
            # build up the list of tests that can be run by parsing docstrings
            for tpath in path_dir.glob("*.py"):

                # parse the test file using ast
                with open(tpath) as f:
                    mod = ast.parse(f.read())

                function_definitions = [node for node in mod.body if isinstance(node, ast.FunctionDef)]
                for func in function_definitions:
                    docstr = ast.get_docstring(func)
                    snippets = load_tests_from_docstring(docstr)
                    for s in snippets:
                        id_test_map[s.id] = s

                classes = [node for node in mod.body if isinstance(node, ast.ClassDef)]
                for class_ in classes:
                    methods = [node for node in class_.body if isinstance(node, ast.FunctionDef)]
                    for func in methods:
                        docstr = ast.get_docstring(func)
                        snippets = load_tests_from_docstring(docstr)
                        for s in snippets:
                            id_test_map[s.id] = s
                    class_docstr = ast.get_docstring(class_)
                    snippets = load_tests_from_docstring(class_docstr)
                    for s in snippets:
                        id_test_map[s.id] = s

        for path_dir in self._get_dirs():
            for tpath in path_dir.glob("*.yea"):
                # TODO: parse yea file looking for path info
                spec = testspec.load_yaml_from_file(tpath)
                id_not_in_map = spec.get("id", None) not in id_test_map
                test_selected_to_run = all_tests or str(tpath) in args_tests

                if id_not_in_map or not test_selected_to_run:
                    logger.debug("skip yea fname: {}".format(tpath))
                    continue

                if all_tests:
                    if spec.get("tag", {}).get("skip", False):
                        continue
                    suite = spec.get("tag", {}).get("suite", "main")
                    shard = spec.get("tag", {}).get("shard", "default")
                    if self._args.suite and self._args.suite != suite:
                        continue
                    if self._args.shard and self._args.shard != shard:
                        continue

                # write test and spec to tempfiles
                shutil.copy(tpath, self._tmpdir)
                t_fname = self._tmpdir / tpath.name
                py_fname = str(t_fname)[:-4] + ".py"
                with open(py_fname, "w") as f:
                    f.write(id_test_map[spec["id"]].code)

                # add .yea or .py file
                tpaths.append(pathlib.Path(py_fname))

        tlist = []
        for tname in tpaths:
            t = ytest.YeaTest(tname=tname, yc=self._yc)
            test_perms = t.get_permutations()
            tlist.extend(test_perms)

        tlist.sort(key=alphanum_sort)
        self._test_list = tlist

    def _runall(self):
        for t in self._test_list:
            self._yc.monitors_reset()
            t.run()
            self._capture_result(t)

    def _check_dict(self, result, s, expected, actual):
        if expected is None:
            return
        for k, v in actual.items():
            exp = expected.get(k)
            if exp != v:
                result.append("BAD_{}({}:{}!={})".format(s, k, exp, v))
        for k, v in expected.items():
            act = actual.get(k)
            if v != act:
                result.append("BAD_{}({}:{}!={})".format(s, k, v, act))

    def _capture_result(self, t):
        test_cfg = t._test_cfg
        if not test_cfg:
            return
        if self._yc.is_live():
            # we are live
            return
        result = self._yc.test_check(t)
        # print("GOTRES", result)
        result_str = ",".join(result)
        # self._results[t._tname] = result_str
        elapsed = t._time_end - t._time_start
        tc = junit_xml.TestCase(t.test_id, classname="yea_func", elapsed_sec=elapsed)
        if result_str:
            tc.add_failure_info(message=result_str)
        self._results.append(tc)

    def run(self):
        try:
            self._populate()
            # inform so we only start monitors needed
            self._yc.monitors_inform(self.get_tests())
            self._yc.monitors_init()
            self._yc.monitors_start()
            self._runall()
            self.finish()
        finally:
            self._yc.monitors_stop()

    def _save_results(self):
        res_fname = self._yc._cfg._results_file
        if not res_fname:
            return
        p = self._yc._cfg._cfroot.joinpath(res_fname)
        ts = junit_xml.TestSuite("yea-func", self._results)
        # create testfile dir if it doesnt exist
        testdir = p.parent  # get the directory portion of path
        testdir.mkdir(parents=True, exist_ok=True)
        with open(p, "w") as f:
            junit_xml.TestSuite.to_file(f, [ts], prettyprint=False, encoding="utf-8")

    def finish(self):
        self.clean()
        self._save_results()
        exit_code = 0
        print("\nResults:")
        print("--------")
        if not self._results:
            sys.exit(exit_code)
        tlen = max([len(tc.name) for tc in self._results])
        for tc in self._results:
            # TODO: fix hack that only looks at first message
            r = tc.failures[0]["message"] if tc.failures else ""
            emoji = "😃"
            if r:
                emoji = '🐴 "Neigh" -- '

            print("  {:<{}s}: {}{}".format(tc.name, tlen, emoji, r))
            if r:
                exit_code = 1
        sys.exit(exit_code)

    def get_tests(self):
        return self._test_list
