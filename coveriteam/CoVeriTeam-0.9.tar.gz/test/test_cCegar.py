# This file is part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
# https://gitlab.com/sosy-lab/software/coveriteam
#
# SPDX-FileCopyrightText: 2021 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

import coveriteam.util as util
import pathlib
import sys
from contextlib import contextmanager
from io import StringIO
from typing import NamedTuple, Sequence
import importlib
from nose import SkipTest


class Run(NamedTuple):
    cmdline: str
    output: Sequence[str]


# from https://stackoverflow.com/a/17981937/3012884
@contextmanager
def capture_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


script = pathlib.Path(__file__).resolve()
project_dir = script.parent
lib_dir = project_dir.parent / "lib"
for wheel in lib_dir.glob("*.whl"):
    sys.path.insert(0, str(wheel))
sys.path.insert(0, str(project_dir))

import benchexec

benchexec_toolinfo = importlib.import_module(
    "benchexec.tools.coveriteam-verifier-validator"
)


from coveriteam.coveriteam import CoVeriTeam

DIR_EXAMPLES = pathlib.Path("examples")
DIR_TEST_DATA = DIR_EXAMPLES / "test-data"
DIR_PROGRAMS = DIR_TEST_DATA / "c"
PATH_UNREACH_PROP = DIR_TEST_DATA / "properties" / "unreach-call.prp"
DIR_CCEGAR = DIR_EXAMPLES / "Component-based_CEGAR"


def setup_module():
    util.set_cache_directories()


def _run_and_check_verdict(inputs, expected_verdict):
    with capture_output() as (out, err):
        CoVeriTeam().start(inputs)
    run = Run(cmdline=" ".join(inputs), output=out.getvalue().splitlines())
    verdict = benchexec_toolinfo.Tool().determine_result(run)
    assert verdict == expected_verdict, (
        f"Actual verdict '{verdict}' != '{expected_verdict}' (expected)\nRecorded CoVeriTeam output:\n"
        + "\n".join(run.output)
    )


def test_cCegar_proves_in_first_iteration_sanfoundry_43_ground():
    compositions = DIR_CCEGAR.glob("*.cvt")
    for composition in compositions:
        yield _check_cCegar_proves, composition, DIR_PROGRAMS / "sanfoundry_43_ground.i"


def _check_cCegar_proves(composition, program):
    inputs = [str(composition)]
    inputs += ["--input", f"program_path={program}"]
    inputs += ["--input", f"specification_path={PATH_UNREACH_PROP}"]
    inputs += ["--data-model", "ILP32"]
    _run_and_check_verdict(inputs, expected_verdict=benchexec.result.RESULT_TRUE_PROP)


def test_cCegar_violation_in_first_iteration_error():
    compositions = DIR_CCEGAR.glob("*.cvt")
    for composition in compositions:
        yield _check_cCegar_violation, composition, DIR_PROGRAMS / "error.i"


def _check_cCegar_violation(composition, program):
    if "symbiotic" in composition.name.lower() and sys.version_info[1] != 8:
        # symbiotic only runs on python 3.8
        raise SkipTest()
    inputs = [str(composition)]
    inputs += ["--input", f"program_path={program}"]
    inputs += ["--input", f"specification_path={PATH_UNREACH_PROP}"]
    inputs += ["--data-model", "ILP32"]
    _run_and_check_verdict(inputs, expected_verdict=benchexec.result.RESULT_FALSE_REACH)


def test_cCegar_prove_multiple_cycles():
    compositions = [
        "cCegar-predmap_cex-cpachecker_ref-cpachecker.cvt",
        "cCegar-invariantWitness_cex-cpachecker_ref-cpachecker.cvt",
    ]
    for composition in [DIR_CCEGAR / c for c in compositions]:
        yield _check_cCegar_proves, composition, DIR_PROGRAMS / "jain_1-1.c"


def test_cCegar_violation_multiple_cycles():
    compositions = [
        "cCegar-predmap_cex-cpachecker_ref-cpachecker.cvt",
        "cCegar-invariantWitness_cex-cpachecker_ref-cpachecker.cvt",
    ]
    for composition in [DIR_CCEGAR / c for c in compositions]:
        yield _check_cCegar_violation, composition, DIR_PROGRAMS / "rangesum.i"
