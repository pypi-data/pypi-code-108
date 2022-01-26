# This file is part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
# https://gitlab.com/sosy-lab/software/coveriteam
#
# SPDX-FileCopyrightText: 2020 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

from coveriteam.language import CoVeriLangException
import uuid
import coveriteam.util as util
import os
import io
import sys
import logging
from xml.etree import ElementTree
from xml.dom import minidom
from coveriteam.util import str_dict, CVT_DEBUG_LEVEL
from pathlib import Path

RESULT_XML_PUBLIC_ID = "+//IDN sosy-lab.org//DTD CoVeriTeam result 0.1//EN"
RESULT_XML_SYSTEM_ID = "https://www.sosy-lab.org/coveriteam/result-0.1.dtd"


class Actor:
    _actor_execution_id = ""

    def __init__(self):
        self._xml_elem = None

    @property
    def xml_elem(self):
        return self._xml_elem

    @xml_elem.setter
    def xml_elem(self, e):
        self._xml_elem = e

    def name(self):
        """
        Return the name of the actor, formatted for humans.
        This function should always be overriden.
        @return a non-empty string
        """
        return "UNKOWN"

    def get_actor_kind():
        """
        Returns the kind of the actor.
        """
        return ""

    def get_input_artifacts(self):
        return self._input_artifacts

    def get_output_artifacts(self):
        return self._output_artifacts

    def act_and_save_xml(self, **kwargs):
        Actor._actor_execution_id = str(uuid.uuid4())
        # The default for exist_ok is False but still writing it explicitly.
        # This dir is supposed to be unique, so it must not exist.
        Actor.get_top_actor_execution_dir().mkdir(exist_ok=False, parents=True)
        try:
            res = self.act(**kwargs)
            self.save_xml()
            self.create_symlink_for_last_execution()
            return res
        except CoVeriLangException as e:
            logging.error(
                "Could not successfully complete execution due to the following error:"
            )
            logging.exception(e)
            logging.error("\n Exiting CoVeriTeam...........")
            sys.exit()

    @staticmethod
    def _get_relative_path_to_actor(path):
        actor_path = Actor.get_top_actor_execution_dir()
        return os.path.relpath(path, actor_path) if path else ""

    @staticmethod
    def get_top_actor_execution_dir():
        return util.LOG_DIR / Actor._actor_execution_id

    def act(self, **kwargs):
        """This function acts on the input artifacts to produce output artifacts.
        First it checks the types of the inputs provided, then calls _act, and
        then again checks the types of outputs produced by _act.

        The definition of _act has to be provided by the implementing classes.
        """
        logging.log(
            CVT_DEBUG_LEVEL,
            "Executing actor %r with parameters %r",
            self.name(),
            kwargs,
        )
        self._type_check_inputs(kwargs)
        res = self._act(**kwargs)
        self._type_check_outputs(res)
        self.gen_xml_elem(inputs=kwargs, outputs=res)

        logging.log(
            CVT_DEBUG_LEVEL,
            "Actor %s acted on artifacts:\n %s \nand produced artifacts:\n %s",
            self.name(),
            str_dict(kwargs),
            str_dict(res),
        )

        return res

    def _type_check_inputs(self, kwargs):
        # TODO Check covariance and contravariance issues
        ia = self.get_input_artifacts()
        if len(kwargs) != len(ia):
            raise CoVeriLangException(
                "Type Check failed for inputs in actor with name {}. "
                "Mismatch of number of artifacts provided with number of required "
                "artifacts. Provided = {}, and required = {}. \n Provided Artifacts: {}"
                "\nRequired Artifacts: {}".format(
                    self.name(),
                    len(kwargs),
                    len(ia),
                    list(kwargs.keys()),
                    list(ia.keys()),
                )
            )
        for key, artifactValue in kwargs.items():
            expected_type = ia.get(key)
            if expected_type is None or not isinstance(artifactValue, expected_type):
                raise CoVeriLangException(
                    "Type Check failed for inputs in actor with name {}. "
                    "Type mismatch for the input artifact name: {}. "
                    "\nvalue: {}, type: {}, expected type: {}".format(
                        self.name(),
                        key,
                        artifactValue,
                        type(artifactValue),
                        expected_type,
                    )
                )

    def _type_check_outputs(self, kwargs):
        logging.log(CVT_DEBUG_LEVEL, f"Performing type check for {self.name()}")
        # TODO Check covariance and contravariance issues
        oa = self.get_output_artifacts()
        if len(kwargs) != len(oa):
            raise CoVeriLangException(
                "Type Check failed for outputs in actor with name {}. "
                "Mismatch of number of artifacts provided with number of required "
                "artifacts. Provided = {}, and required = {}. \n Provided Artifacts: {}"
                "\nRequired Artifacts: {}".format(
                    self.name(),
                    len(kwargs),
                    len(oa),
                    list(kwargs.keys()),
                    list(oa.keys()),
                )
            )
        for key, artifactValue in kwargs.items():
            expected_type = oa.get(key)
            if expected_type is None or not isinstance(artifactValue, expected_type):
                raise CoVeriLangException(
                    "Type Check failed for outputs in actor with name {}. "
                    "Type mismatch for the output artifact name: {}. "
                    "\nvalue: {}, type: {}, expected type: {}".format(
                        self.name(),
                        key,
                        artifactValue,
                        type(artifactValue),
                        expected_type,
                    )
                )

    def __str__(self):
        # TODO this is valid only for atomic actors. So, maybe move it there.
        outstr = type(self).get_actor_kind() + " :: " + self.name()
        outstr += self.__get_actor_type_str__()
        return outstr

    def __get_actor_type_str__(self):
        def pp(d):
            return {k: d[k].__name__ for k in d.keys()}

        outstr = " :: " + str(pp(self.get_input_artifacts()))
        outstr += " --> " + str(pp(self.get_output_artifacts()))
        return outstr

    def gen_xml_elem(self, inputs, outputs, **kwargs):
        logging.log(CVT_DEBUG_LEVEL, f"Creating xml for {self.name()}")
        # TODO sysinfo
        # TODO measurements
        # By this time we can safely assume that the actual inputs and outputs are compliant to the type.
        ip = ElementTree.Element("inputs")
        for key, val in inputs.items():
            t = self.get_input_artifacts().get(key)
            # TODO note: str(val), and t.__name__ might need to change. It is OK at the moment, but at some point it might not work
            # str(val) might not be enough for all cases, and t.__name__ is just ugly
            ip_elem = ElementTree.Element("input", {"name": key, "type": t.__name__})
            if isinstance(val.path, str):
                ip_elem.text = Actor._get_relative_path_to_actor(val.path)
            elif isinstance(val.path, list):
                s = []
                for p in val.path:
                    s += [Actor._get_relative_path_to_actor(p)]
                ip_elem.text = str(s)

            ip.append(ip_elem)

        op = ElementTree.Element("outputs")
        for key, val in outputs.items():
            t = self.get_output_artifacts().get(key)
            assert t is not None, f"Missing output artifact for {key} (value: {val})"
            op_elem = ElementTree.Element("output", {"name": key, "type": t.__name__})
            if val.path:
                op_elem.text = Actor._get_relative_path_to_actor(val.path)
            else:
                op_elem.text = str(val)
            op.append(op_elem)

        actorElem = ElementTree.Element("actor", {"name": self.name()})
        actorElem.append(ip)
        actorElem.append(op)
        self.xml_elem = actorElem

    def save_xml(self):
        xml_path = Actor.get_top_actor_execution_dir() / "execution_trace.xml"
        with io.TextIOWrapper(xml_path.open("wb"), encoding="utf-8") as file:
            rough_string = ElementTree.tostring(self.xml_elem, encoding="unicode")
            reparsed = minidom.parseString(rough_string)
            doctype = minidom.DOMImplementation().createDocumentType(
                "result", RESULT_XML_PUBLIC_ID, RESULT_XML_SYSTEM_ID
            )
            reparsed.insertBefore(doctype, reparsed.documentElement)
            reparsed.writexml(
                file, indent="", addindent="  ", newl="\n", encoding="utf-8"
            )

    def create_symlink_for_last_execution(self):
        last = Path("lastexecution")
        if last.is_symlink() or last.exists():
            last.unlink()

        last.symlink_to(Actor.get_top_actor_execution_dir())

    def stop(self):
        """
        Performs a clean stop of this actor.
        There is no guarantee for an produced artifact.
        """
        raise CoVeriLangException(
            "I shouldn't have been called. "
            "This means that there is an inheriting class that has not implemented me: "
            "the stop function. "
            "All classes inheriting from Actor should implement the stop function."
        )


class Analyzer(Actor):
    # Analyzer should always take a program, spec, and produce a verdict and a justification.
    # But the problem is that this is true only for the verification analyzers. Testing analyzers
    # have a different story. They do not provide justification and also may provide a number in case
    # testCov.

    def get_actor_kind():
        return "Analyzer"


class Transformer(Actor):
    def get_actor_kind():
        return "Transformer"


class Verifier(Analyzer):
    def get_actor_kind():
        return "Verifier"


class Validator(Analyzer):
    def get_actor_kind():
        return "Validator"


class TestGenerator(Analyzer):
    def get_actor_kind():
        return "TestGenerator"


class Instrumentor(Transformer):
    def get_actor_kind():
        return "Instrumentor"


class Reducer(Transformer):
    def get_actor_kind():
        return "Reducer"
