# This file is part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
# https://gitlab.com/sosy-lab/software/coveriteam
#
# SPDX-FileCopyrightText: 2020 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

from coveriteam.language.actor import Actor
from coveriteam.language.artifact import (
    Artifact,
    Joinable,
    Specification,
    TestSpecification,
    Comparable,
    ClassificationConfidence,
    AtomicActorDefinition,
)
from coveriteam.util import filter_dict, rename_dict
from coveriteam.util import INPUT_FILE_DIR
from coveriteam.language import CoVeriLangException


class UtilActor(Actor):
    def __init__(self):
        super().__init__()

    def get_actor_kind():
        return "UtilityActor"

    def stop(self):
        return


class IdentityActor(UtilActor):
    def name(self):
        return "Identity"

    def __init__(self, a: Actor):
        super().__init__()
        self._input_artifacts = a.get_input_artifacts()
        self._output_artifacts = a.get_output_artifacts()
        # TODO as a projection actor the outputs should be a subset of the inputs

    def _act(self, **kwargs):
        return filter_dict(kwargs, self.get_output_artifacts())


class CopyActor(UtilActor):
    def name(self):
        return "Identity"

    # TODO Should have an option for renaming
    def __init__(self, names):
        super().__init__()
        if type(names) is set:
            # The case where only a list of artifact to copy is provided.
            self._renaming_map = {}
            self._input_artifacts = {a: Artifact for a in names}
            self._output_artifacts = {a: Artifact for a in names}
        elif type(names) is dict:
            # the mapping should either all be renaming or on artifact types
            if len({type(e) for e in names.values()}) != 1:
                raise CoVeriLangException(
                    "This feature is not supported in the copy actor!"
                )
            if all(isinstance(e, tuple) for e in names) and all(
                type(e) is str for e in names.values()
            ):
                self._renaming_map = {
                    old[0]: new_name for old, new_name in names.items()
                }
                self._input_artifacts = {
                    name: artifact_type for name, artifact_type in names
                }
                self._output_artifacts = {
                    new_name: old[1] for old, new_name in names.items()
                }
            elif all(type(e) is str for e in names.values()):
                # The case where the artifacts should be copied and renamed.
                self._renaming_map = names
                self._input_artifacts = {a: Artifact for a in names.keys()}
                self._output_artifacts = {a: Artifact for a in names.values()}
            else:
                # The case where artifact and its type is provided
                self._renaming_map = {}
                self._input_artifacts = names
                self._output_artifacts = names
        else:
            raise CoVeriLangException(
                "This feature is not supported in the copy actor!"
            )

    def _act(self, **kwargs):
        return rename_dict(kwargs, self._renaming_map)


# TODO delete by Jan 2021 if still commented.
"""
class SimpleExpressionActor(UtilActor):
    def name(self):
        return "SimpleExpressionActor"

    # TODO Should have an option for renaming
    def __init__(self, inputs, outputs, exp):
        self._input_artifacts = inputs
        self._output_artifacts = outputs
        self.exp = exp

    def _act(self, **kwargs):
        return eval(self.exp, globals(), {**kwargs})
"""


class Setter(UtilActor):
    def name(self):
        return "Setter"

    def __init__(self, artifact_name, value):
        super().__init__()
        self._input_artifacts = {artifact_name: type(value)}
        self._output_artifacts = self._input_artifacts
        self._output = artifact_name
        self.value = value

    def _act(self, **kwargs):
        return {self._output: self.value}


class Joiner(UtilActor):
    def name(self):
        return "Joiner"

    def __init__(self, t, ips, op):
        super().__init__()
        # TODO Ideally this type could be inferred in the composition
        assert issubclass(t, Joinable), "%r is not Joinable" % t
        self._input_artifacts = {ip: t for ip in ips}
        self._output_artifacts = {op: t}
        self.op = op

    def _act(self, **kwargs):
        ips = list(self._input_artifacts.keys())
        joined = kwargs[ips[0]].join(kwargs[ips[1]])
        return {self.op: joined}


class TestSpecToSpec(UtilActor):
    def name(self):
        return "TestSpecToSpec"

    def __init__(self):
        super().__init__()
        self._input_artifacts = {"test_spec": TestSpecification}
        self._output_artifacts = {"spec": Specification}

    def _act(self, **kwargs):
        # At the moment this works because we have only one test specification.
        # The day we add more this might stop working.
        property_path = INPUT_FILE_DIR + "specifications/unreach-call.prp"
        return {"spec": Specification(property_path)}


class SpecToTestSpec(UtilActor):
    def name(self):
        return "SpecToTestSpec"

    def __init__(self):
        super().__init__()
        self._input_artifacts = {"spec": Specification}
        self._output_artifacts = {"test_spec": TestSpecification}

    def _act(self, **kwargs):
        # At the moment this works because we have only one test specification.
        # The day we add more this might stop working.
        property_path = INPUT_FILE_DIR + "specifications/coverage-error-call.prp"
        return {"test_spec": TestSpecification(property_path)}


class Comparator(UtilActor):
    def name(self):
        return "Comparator"

    def __init__(self, t, ips, op):
        # TODO Ideally this type could be inferred in the composition
        assert issubclass(t, Comparable), "%r is not Comparable" % t
        self._input_artifacts = {ip: t for ip in ips}
        self._output_artifacts = {op: t}
        self.op = op

    def _act(self, **kwargs):
        largest = max(list(kwargs.values()))
        return {self.op: largest}


class ClassificationToActorDefinition(UtilActor):
    def name(self):
        return "ClassificationToActorDefinition"

    def __init__(self):
        self._input_artifacts = {"classification": ClassificationConfidence}
        self._output_artifacts = {"actordef": AtomicActorDefinition}

    def _act(self, **kwargs):
        classification = kwargs["classification"]
        return {"actordef": AtomicActorDefinition(classification.clazz)}
