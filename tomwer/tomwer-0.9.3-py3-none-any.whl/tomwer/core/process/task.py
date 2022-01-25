# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/
"""
Define the tomwer Task class.
Insure connection with ewoks.
All instances of tomwer Tasks should avoid gui import (as qt).
"""


__author__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "27/07/2021"


import h5py
import numpy
from datetime import datetime
from typing import Union
from silx.io.dictdump import dicttoh5
from collections import namedtuple
from silx.io.dictdump import h5todict
from tomoscan.io import HDF5File
import typing
import logging
from silx.io.utils import h5py_read_dataset
import multiprocessing
import silx
from ewokscore.task import Task as EwoksTask


mult_manager = multiprocessing.Manager()


_logger = logging.getLogger(__name__)

# TODO: should be removed
_input_desc = namedtuple("_input_desc", ["name", "type", "handler", "doc"])
# TODO: should be removed

_output_desc = namedtuple("_output_desc", ["name", "type", "doc"])

_process_desc = namedtuple(
    "_process_desc", ["process_order", "configuration", "results"]
)


_MULTIPROCESSING_LOCKERS = mult_manager.dict()


class BaseProcessInfo:
    """Tomwer base process class"""

    MULTIPROCESSING_LOCKERS = mult_manager.dict()

    _output_values = {}
    # TODO: look at this: not sure this is needed anymore

    def __init__(self, inputs=None):
        if inputs is None:
            inputs = {}
        self._scheme_title = inputs.get(
            "scheme_title", None
        )  # title of the associated scheme
        self._return_dict = inputs.get("return_dict", False)

        """should the return type of the handler should be TomoBase instance
        objects or dict"""
        self._settings = {}

    @staticmethod
    def _get_lock(file_name):
        if file_name not in _MULTIPROCESSING_LOCKERS:
            _MULTIPROCESSING_LOCKERS[file_name] = mult_manager.Lock()
        return _MULTIPROCESSING_LOCKERS[file_name]

    @staticmethod
    def properties_help():
        """

        :return: display the list of all managed keys and possible values
        :rtype: str
        """
        # TODO: use argsparse instead of this dict ?
        raise NotImplementedError("BaseProcess is an abstract class")

    def get_output_value(self, key):
        """

        :param str key:
        :return:
        """
        assert type(key) is str
        if key in self._output_values:
            return self._output_values[key]
        else:
            return None

    def clear_output_values(self):
        self._output_values.clear()

    def register_output(self, key, value):
        """

        :param str key: name of the output
        :param value: value of the output
        """
        self._output_values[key] = value

    def key_exist(self, key):
        for _output in self.outputs:
            if _output.name == key:
                return True
        return False

    @staticmethod
    def program_name():
        """Name of the program used for this processing"""
        raise NotImplementedError("Base class")

    @staticmethod
    def program_version():
        """version of the program used for this processing"""
        raise NotImplementedError("Base class")

    @staticmethod
    def definition():
        """definition of the process"""
        raise NotImplementedError("Base class")

    def get_configuration(self) -> Union[None, dict]:
        """

        :return: configuration of the process
        :rtype: dict
        """
        if self._settings is None:
            return None
        if len(self._settings) > 0:
            return self._settings
        else:
            return None

    def set_configuration(self, configuration: dict) -> None:
        self._settings = configuration

    def register_process(
        self,
        process_file: str,
        entry: str,
        configuration: Union[dict, None],
        results: Union[dict, None],
        process_index: int,
        interpretations: Union[dict, None] = None,
        overwrite: bool = True,
    ) -> None:
        """
        Store the current process in the linked h5 file if any,
        output data stored will be the one defined by the data_keys

        :param process_file: where to store the processing information
        :type process_file: str
        :param str entry: entry process
        :param configuration: configuration of the process
        :type configuration: Union[dict,None]
        :param results: result of the processing
        :type: Union[dict,None]
        :param process_index: index of the process
        :type process_index: int
        :param bool overwrite: if True then overwrite the process if already
                               exists
        :param interpretations: for each result we can add a flag
                                'interpretation'
        :type interpretations: Union[None, dict
        """
        assert process_file is not None
        try:
            self._register_process(
                process_file=process_file,
                entry=entry,
                process=self,
                configuration=configuration,
                results=results,
                process_index=process_index,
                interpretations=interpretations,
                overwrite=overwrite,
            )
        except IOError as e:
            _logger.error(e)

    @staticmethod
    def _register_process(
        process_file: str,
        process,
        entry: typing.Union[str, None],
        configuration: Union[dict, None],
        results: Union[dict, None],
        process_index: int,
        interpretations: Union[dict, None] = None,
        overwrite: bool = True,
    ) -> None:
        """
        Store the current process in the linked h5 file if any,
        output data stored will be the one defined by the data_keys

        :param process: process to record
        :param process_file: where to store the processing information
        :type process_file: str
        :param Union[str, None] entry: entry process
        :param configuration: configuration of the process
        :type configuration: Union[dict,None]
        :param results: result of the processing
        :type: Union[dict,None]
        :param process_index: index of the process
        :type process_index: int
        :param bool overwrite: if True then overwrite the process if already
                               exists
        :param interpretations: for each result we can add a flag
                                'interpretation'
        :type interpretations: Union[None, dict
        """
        assert process_file is not None, "The process file should be defined"
        if interpretations is None:
            interpretations = {}
        process_name = "tomwer_process_" + str(process_index)

        def get_process_path():
            return "/".join((entry or "entry", process_name))

        # save it to the file
        with Task._get_lock(process_file):
            # needs an extra lock for multiprocessing

            with HDF5File(process_file, mode="a") as h5f:
                nx_process = h5f.require_group(get_process_path())
                if "NX_class" not in nx_process.attrs:
                    nx_process.attrs["NX_class"] = "NXprocess"
                if overwrite:
                    for key in (
                        "program",
                        "results",
                        "version",
                        "date",
                        "sequence_index",
                        "class_instance",
                    ):
                        if key in nx_process:
                            del nx_process[key]

                # write process information
                nx_process["program"] = process.program_name()
                nx_process["version"] = process.program_version()
                nx_process["date"] = datetime.now().replace(microsecond=0).isoformat()
                nx_process["sequence_index"] = numpy.int32(process_index)
                _class = process.__class__
                nx_process["class_instance"] = ".".join(
                    (_class.__module__, _class.__name__)
                )

            # dump result
            if results is not None:
                h5path = "/".join((get_process_path(), "results"))
                if silx.version >= "0.15":
                    dicttoh5(
                        results,
                        h5file=process_file,
                        h5path=h5path,
                        update_mode="modify",
                        mode="a",
                    )
                else:
                    dicttoh5(
                        results,
                        h5file=process_file,
                        h5path=h5path,
                        overwrite_data=True,
                        mode="a",
                    )
                for interpretation_key, interpretation in interpretations.items():
                    try:
                        with HDF5File(process_file, mode="a") as h5f:
                            node = h5f["/".join((get_process_path(), "results"))]
                            node[interpretation_key].attrs[
                                "interpretation"
                            ] = interpretation
                    except KeyError:
                        _logger.warning(
                            "Invalid interpretation - no result store"
                            " for %s" % interpretation_key
                        )

            # dump configuration
            if configuration is not None:
                h5path = "/".join((get_process_path(), "configuration"))
                if silx.version >= "0.15":
                    dicttoh5(
                        configuration,
                        h5file=process_file,
                        h5path=h5path,
                        update_mode="modify",
                        mode="a",
                    )
                else:
                    dicttoh5(
                        configuration,
                        h5file=process_file,
                        h5path=h5path,
                        overwrite_data=True,
                        mode="a",
                    )

                with HDF5File(process_file, mode="a") as h5f:
                    nx_process = h5f.require_group(get_process_path())
                    nx_process["configuration"].attrs["NX_class"] = "NXcollection"

    @staticmethod
    def _get_process_nodes(
        root_node: h5py.Group, process, version: str = None, depth: int = 2
    ) -> dict:
        """

        :param root_node:
        :param version: version to look for (ignored for now)
        :return: list of process nodes [as h5py.Group]. Key is node name,
                 value is the process index
        """

        def is_process_node(node):
            if node is None:
                return False
            return (
                node.name.split("/")[-1].startswith("tomwer_process_")
                and "NX_class" in node.attrs
                and node.attrs["NX_class"] == "NXprocess"
                and "program" in node
                and (
                    process is None
                    or h5py_read_dataset(node["program"]) == process.program_name()
                )
                and "version" in node
                and "sequence_index" in node
            )

        if isinstance(root_node, h5py.Dataset):
            return {}
        res = {}
        if is_process_node(root_node):
            res[root_node.name] = int(h5py_read_dataset(root_node["sequence_index"]))

        if root_node is not None:
            for _, node in root_node.items():
                if depth >= 1:
                    res.update(
                        Task._get_process_nodes(
                            process=process,
                            root_node=node,
                            depth=depth,
                            version=version,
                        )
                    )
        return res

    @staticmethod
    def get_most_recent_process(
        root_node: h5py.Group, process, version: str = None
    ) -> Union[None, h5py.Group]:
        nodes = Task._get_process_nodes(
            root_node=root_node, process=process, version=version, depth=1
        )
        nodes_with_time = []
        nodes_time = []
        import datetime

        for node_name in nodes:
            node = root_node[node_name]
            assert isinstance(node, h5py.Group), "node should be a h5py.Group"
            if "date" in node:
                nodes_with_time.append(node)
                nodes_time.append(
                    datetime.datetime.fromisoformat(h5py_read_dataset(node["date"]))
                )
        if len(nodes_with_time) == 0:
            return None
        else:
            st = numpy.argmax(nodes_time)
            return nodes_with_time[st]

    @staticmethod
    def get_processes_frm_type(process_file: str, process_type, entry=None) -> list:
        """

        :param str process_file: file to read
        :param process_type: process type we are looking for
        :return: list of _process_desc(sequence_index, configuration, results)
        :rtype: list
        """
        processes = []
        with HDF5File(process_file, mode="r", swmr=True) as h5f:
            if entry is None:
                if len(h5f.keys()) > 0:
                    root = h5f[list(h5f.keys())[0]]
                else:
                    _logger.warning("no process find")
            else:
                root = h5f[entry]
            for process in root.keys():
                nx_process = root[process]
                if (
                    h5py_read_dataset(nx_process["program"])
                    == process_type.program_name()
                ):
                    p_order = h5py_read_dataset(nx_process["sequence_index"])
                    config = h5todict(
                        process_file, "/".join((nx_process.name, "configuration"))
                    )
                    results = h5todict(
                        process_file, "/".join((nx_process.name, "results"))
                    )
                    processes.append(
                        _process_desc(
                            process_order=p_order, configuration=config, results=results
                        )
                    )
        return processes

    def _set_return_dict(self, return_dict):
        """

        :param bool return_dict: if True, force the process to return a dict
                                 instead of a `.TomoBase` object
        """
        self._return_dict = return_dict


class Task(EwoksTask, BaseProcessInfo):
    """Class from which all tomwer process should inherit

    :param logger: the logger used by the class
    """

    def __init__(self, varinfo=None, inputs=None, label=None):
        BaseProcessInfo.__init__(self, inputs=inputs)
        EwoksTask.__init__(self, varinfo=varinfo, inputs=inputs, label=label)
