# This file is part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
# https://gitlab.com/sosy-lab/software/coveriteam
#
# SPDX-FileCopyrightText: 2020 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

from coveriteam.actors.analyzers import ProgramVerifier
from coveriteam.actors.misc import (
    WitnessInstrumentor,
    WitnessToTest,
    TestGoalAnnotator,
    TestGoalPruner,
    TestGoalExtractor,
    TestCriterionInstrumentor,
)
from coveriteam.language.artifact import TestGoal
from coveriteam.language.composition import Sequence, ITE, Parallel, Iterative
from coveriteam.language.utilactors import (
    Joiner,
    IdentityActor,
    TestSpecToSpec,
    CopyActor,
)


# This is something what a user will write. DSL should be able to do this.
def validated_verifier(ver, val):
    cond = "verdict in [RESULT_CLASS_FALSE, RESULT_CLASS_TRUE]"

    ch = ITE(cond, val, IdentityActor(val))

    return Sequence(ver, ch)


def metaval_prototype():
    witness_instrumentor = WitnessInstrumentor("actors/cpa-witnesses-instrumentor.yml")

    # In termination only false is verified
    cond_termination = "isinstance(spec, BehaviorSpecification)"
    ua = ProgramVerifier("actors/uautomizer.yml")
    ch_termination = ITE(cond_termination, ua, IdentityActor(ua))

    cond_no_overflow = "isinstance(spec, BehaviorSpecification)"
    ch_no_overflow = ITE(
        cond_no_overflow, ProgramVerifier("actors/uautomizer.yml"), ch_termination
    )

    cond_mem_safety = "isinstance(spec, BehaviorSpecification)"
    ch_mem_safety = ITE(
        cond_mem_safety, ProgramVerifier("actors/symbiotic.yml"), ch_no_overflow
    )

    cond_reach_safety = "isinstance(spec, BehaviorSpecification)"
    ch_reach_safety = ITE(
        cond_reach_safety, ProgramVerifier("actors/cpa-seq.yml"), ch_mem_safety
    )

    metaval = Sequence(witness_instrumentor, ch_reach_safety)

    return metaval


def conditional_tester(test_generator):
    pruner = TestGoalPruner("actors/test-goal-pruner.yml")
    extractor = TestGoalExtractor("actors/test-goal-extractor.yml")

    test_gen = Sequence(pruner, test_generator)

    joiner = Joiner(TestGoal, ["covered_goals", "extracted_goals"], "covered_goals")
    ext_and_joiner = Sequence(extractor, joiner)

    last_actor = Parallel(ext_and_joiner, CopyActor(["test_suite"]))
    print(Sequence(test_gen, last_actor))

    return Sequence(test_gen, last_actor)


def verifier_based_tester(ver):
    cond = "verdict in [RESULT_CLASS_FALSE]"

    w2test = WitnessToTest("actors/cpachecker-witness-to-test.yml")

    # TODO following is a hack, the second argument should be a constructor of default output type.
    # TODO This could be removed.
    ch = ITE(cond, w2test, w2test)

    return Sequence(ver, ch)


def conditional_tester_verifier_based(ver):
    annotator = TestGoalAnnotator("actors/test-goal-annotator.yml")
    extractor = TestGoalExtractor("actors/test-goal-extractor.yml")

    """
    Difference to tester based conditional tester:
    1) No first relay actor needed, as the spec used by the verifier is the unreach call.
    """
    c1 = Parallel(annotator, TestSpecToSpec())

    test_gen = Sequence(c1, verifier_based_tester(ver))

    ext_and_joiner = Sequence(
        extractor,
        Joiner(TestGoal, ["covered_goals", "extracted_goals"], "covered_goals"),
    )

    last_actor = Parallel(ext_and_joiner, CopyActor(["test_suite"]))
    print(Sequence(test_gen, last_actor))
    return Sequence(test_gen, last_actor)


def atva_paper_fig_14(ver):
    ct = conditional_tester_verifier_based(ver)
    tc = "covered_goals"
    iterative_ct = Iterative(tc, ct)
    instrumentor = TestCriterionInstrumentor("actors/test-criterion-instrumentor.yml")
    print(Sequence(instrumentor, iterative_ct))
    return Sequence(instrumentor, iterative_ct)
