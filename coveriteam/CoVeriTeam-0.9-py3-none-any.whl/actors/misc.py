# This file is part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
# https://gitlab.com/sosy-lab/software/coveriteam
#
# SPDX-FileCopyrightText: 2020 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

from coveriteam.language.artifact import (
    CProgram,
    Program,
    Condition,
    Witness,
    Specification,
    TestGoal,
    TestSpecification,
    TestSuite,
    AtomicActorDefinition,
    FeatureVector,
    ClassificationConfidence,
)
from coveriteam.language.actor import Actor, Instrumentor, Reducer, Transformer
from coveriteam.language.atomicactor import AtomicActor
from coveriteam.util import create_archive
from benchexec import tooladapter
import os
import logging
from coveriteam.language import CoVeriLangException


class WitnessInstrumentor(Instrumentor, AtomicActor):
    _input_artifacts = {"program": CProgram, "spec": Specification, "witness": Witness}
    _output_artifacts = {"program": CProgram}
    _result_files_patterns = ["**/*.c"]

    def _get_arg_substitutions(self, program, spec, witness):
        return {
            "witness": self._get_relative_path_to_tool(witness.path),
            "spec": self._get_relative_path_to_tool(spec.path),
        }

    def _prepare_args(self, program, spec, witness):
        return [program.path, witness.path]

    def _extract_result(self):
        # extract result
        instrumentedProgram = None
        for file in self.log_dir().glob("**/*.c"):
            instrumentedProgram = CProgram(file)
        return {"program": instrumentedProgram}


class WitnessToTest(AtomicActor):
    _input_artifacts = {"program": CProgram, "spec": Specification, "witness": Witness}
    _output_artifacts = {"test_suite": TestSuite}
    _result_files_patterns = ["**/*.xml"]

    def _prepare_args(self, program, spec, witness):
        options = ["-witness", self._get_relative_path_to_tool(witness.path)]
        return [program.path, spec.path, options]

    def _extract_result(self):
        # We assume that the test generator will succeed and create a directory
        # containing metadata.xml. This directory is the test suite.
        for file in self.log_dir().glob("**/metadata.xml"):
            testSuite = TestSuite(os.path.dirname(file))

        return {"test_suite": testSuite}


class TestCriterionInstrumentor(Instrumentor, AtomicActor):
    _input_artifacts = {"program": CProgram, "test_spec": TestSpecification}
    _output_artifacts = {"program": CProgram}
    _result_files_patterns = ["**/*.c"]

    def _prepare_args(self, program, test_spec):
        return [program.path, test_spec.path]

    def _extract_result(self):
        # extract result
        for file in self.log_dir().glob("**/*.c"):
            instrumentedProgram = CProgram(file)

        return {"program": instrumentedProgram}


class TestGoalPruner(Reducer, AtomicActor):
    _input_artifacts = {
        "program": CProgram,
        "test_spec": TestSpecification,
        "covered_goals": TestGoal,
    }
    _output_artifacts = {"program": CProgram}
    _result_files_patterns = ["**/*.c"]

    def _prepare_args(self, program, test_spec, covered_goals):
        options = []
        if covered_goals.path:
            options += [
                "--covered-labels",
                self._get_relative_path_to_tool(covered_goals.path),
            ]

        return [program.path, test_spec.path, options]

    def _extract_result(self):
        # extract result
        for file in self.log_dir().glob("**/reduced.c"):
            prunedProgram = CProgram(file)

        return {"program": prunedProgram}


class TestGoalAnnotator(Reducer, AtomicActor):
    _input_artifacts = {
        "program": CProgram,
        "test_spec": TestSpecification,
        "covered_goals": TestGoal,
    }
    _output_artifacts = {"program": CProgram}
    _result_files_patterns = ["**/*.c"]

    def _prepare_args(self, program, test_spec, covered_goals):
        options = []
        if covered_goals.path:
            options += [
                "--covered-labels",
                self._get_relative_path_to_tool(covered_goals.path),
            ]
        return [program.path, test_spec.path, options]

    def _extract_result(self):
        # extract result
        for file in self.log_dir().glob("**/reduced.c"):
            annotatedProgram = CProgram(file)

        return {"program": annotatedProgram}


class TestGoalExtractor(Transformer, AtomicActor):
    _input_artifacts = {
        "program": CProgram,
        "test_spec": TestSpecification,
        "test_suite": TestSuite,
    }
    _output_artifacts = {"extracted_goals": TestGoal}
    _result_files_patterns = ["**/*.txt"]

    def _prepare_args(self, program, test_spec, test_suite):
        testzip = os.path.join(os.path.dirname(test_suite.path), "test_suite.zip")
        create_archive(test_suite.path, testzip)
        testzip = self._get_relative_path_to_tool(testzip)
        options = ["--test-suite", testzip]
        return [program.path, test_spec.path, options]

    def _extract_result(self):
        # extract result
        for file in self.log_dir().glob("**/covered_goals.txt"):
            extracted_goals = TestGoal(file)

        return {"extracted_goals": extracted_goals}


class CMCReducer(Transformer, AtomicActor):
    _input_artifacts = {"program": CProgram, "condition": Condition}
    _output_artifacts = {"program": CProgram}
    _result_files_patterns = ["**/*.c"]

    def _prepare_args(self, program, condition):
        options_assm_file = [
            "-setprop",
            "residualprogram.assumptionFile="
            + self._get_relative_path_to_tool(condition.path),
        ]
        options_assm_automaton = [
            "-setprop",
            "AssumptionAutomaton.cpa.automaton.inputFile="
            + self._get_relative_path_to_tool(condition.path),
        ]
        options = options_assm_automaton + options_assm_file
        return [program.path, "", options]

    def _extract_result(self):
        # extract result
        for file in self.log_dir().glob("**/*.c"):
            reducedProgram = CProgram(file)

        return {"program": reducedProgram}


class AlgorithmSelector(AtomicActor):
    _input_artifacts = {"program": CProgram, "spec": Specification}
    _output_artifacts = {"actordef": AtomicActorDefinition}
    _result_files_patterns = []

    def _prepare_args(self, program, spec):
        return [program.path, spec.path]

    def _extract_result(self):
        # TODO this could be put in a pattern
        try:
            with open(self.log_file(), "rt", errors="ignore") as outputFile:
                output = outputFile.readlines()
                # first 6 lines are for logging, rest is output of subprocess, see runexecutor.py for details
                output = output[6:]
        except IOError as e:
            logging.warning("Cannot read log file: %s", e.strerror)
            output = []

        exit_code = self.measurements.get("exitcode")
        output = tooladapter.CURRENT_BASETOOL.RunOutput(output)
        run = tooladapter.CURRENT_BASETOOL.Run(self._cmd, exit_code, output, None)

        actordef = AtomicActorDefinition(self._tool.determine_result(run))
        return {"actordef": actordef}


class DynamicActor(Actor):
    # TODO find a place to put this actor.
    # It is neither an atomic not a composite actor.

    def __init__(self, actorkind):
        super().__init__()
        self.actor_to_execute_class = actorkind
        self._input_artifacts = self.actor_to_execute_class._input_artifacts.copy()
        # Additionally add the actor definition.
        self._input_artifacts.update(actordef=AtomicActorDefinition)
        self._output_artifacts = self.actor_to_execute_class._output_artifacts.copy()

    def name(self):
        return self.actor_to_execute_class.get_actor_kind()

    def _act(self, actordef, **kwargs):
        """
        This should first create an actor based on the actor definition, and then call its _act.
        This should suffice.
        This makes me think it is a composite actor.
        """
        actor_to_execute = self.actor_to_execute_class(actordef.path)
        return actor_to_execute.act(**kwargs)


class ConditionExtractor(Transformer, AtomicActor):
    """
    An actor that takes a C program and a list of coveread goals and generates a condition
    automaton from it. A condition can be used in combination with CPAchecker's reducer.
    """

    _input_artifacts = {
        "program": CProgram,
        "covered_goals": TestGoal,
    }
    _output_artifacts = {"condition": Condition}
    _result_files_patterns = ["**/AssumptionAutomaton.txt"]

    def _prepare_args(self, program, covered_goals):
        options_inputfile = [
            "-setprop",
            "conditional_testing.inputfile="
            + self._get_relative_path_to_tool(covered_goals.path),
        ]

        return [program.path, "", options_inputfile]

    def _extract_result(self):
        for result_file in self.log_dir().glob("**/AssumptionAutomaton.txt"):
            condition = Condition(result_file)

            return {"condition": condition}
        return {"condition": None}


class FeatureVectorEncoder(Transformer, AtomicActor):
    """
    An actor that takes a C program and produces a feature vector.
    """

    # TODO decide if we need spec or not

    _input_artifacts = {
        "program": Program,
        "spec": Specification,
    }
    _output_artifacts = {"feature_vector": FeatureVector}
    __embedding_file = "feature_vector.json"
    _result_files_patterns = [__embedding_file]

    def _prepare_args(self, program, spec):
        return [program.path, spec.path]

    def _extract_result(self):
        for result_file in self.log_dir().glob(self.__embedding_file):
            fv = FeatureVector(result_file)
            return {"feature_vector": fv}

        raise CoVeriLangException("Couldn't find the feature vector!")


class Classifier(AtomicActor):
    _input_artifacts = {"feature_vector": FeatureVector}
    _output_artifacts = {"classification": ClassificationConfidence}
    _result_files_patterns = []

    def _get_arg_substitutions(self, feature_vector):
        return {"feature_vector": self._get_relative_path_to_tool(feature_vector.path)}

    def _prepare_args(self, feature_vector):
        return ["", ""]

    def _extract_result(self):
        try:
            with open(self.log_file(), "rt", errors="ignore") as outputFile:
                output = outputFile.readlines()
                # first 6 lines are for logging, rest is output of subprocess, see runexecutor.py for details
                output = output[6:]
        except IOError as e:
            logging.warning("Cannot read log file: %s", e.strerror)
            output = []

        exit_code = self.measurements.get("exitcode")
        output = tooladapter.CURRENT_BASETOOL.RunOutput(output)
        run = tooladapter.CURRENT_BASETOOL.Run(self._cmd, exit_code, output, None)

        cc = ClassificationConfidence(*self._tool.determine_result(run))
        print(cc.clazz + ": " + cc.confidence)
        return {"classification": cc}
