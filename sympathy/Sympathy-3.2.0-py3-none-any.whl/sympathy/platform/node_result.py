# This file is part of Sympathy for Data.
# Copyright (c) 2017, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import json

import traceback
import collections
import datetime
import sys
import uuid
from typing import Optional

from . import exceptions

from .. utils.prim import limit_traceback
from .. utils import log

node_perf_logger = log.get_logger('node.perf')


class ExceptionInformation(object):
    """Information about a single exception."""

    def __init__(self):
        super(ExceptionInformation, self).__init__()
        self._type = ''
        self._string = ''
        self._node_error = False
        self._node_error_dict = None
        self._trace = []
        self._details = ''
        self._path = []

    @classmethod
    def from_exc_info(cls, limit_filename=None):
        """
        Usage:
        ei = ExceptionInformation.from_exc_info()
        """
        instance = cls()
        type_, value, frame = sys.exc_info()
        instance.set_from_exc_info(type_, value, frame, limit_filename)
        return instance

    def _get_trace_step(self, function, line, filename):
        step = collections.namedtuple(
            'ExceptionTraceStep', ['function', 'line', 'filename'])
        step.function = function
        step.line = line
        step.filename = filename
        return step

    @classmethod
    def from_dict(cls, d):
        if d is None:
            return cls()
        instance = cls()
        instance._type = d['type']
        instance._string = d['string']
        instance._node_error = d['node_error']
        instance._node_error_dict = d['node_error_dict']
        instance._trace = []
        for function, line, filename in d['trace']:
            instance._trace.append(
                instance._get_trace_step(function, line, filename))
        instance._details = d['details']
        instance._path = d['path']
        return instance

    def set_from_exc_info(self, type_, value, frame, limit_filename=None):
        """Set exception information from the output of sys.exc_info()."""
        path = []

        while isinstance(value, exceptions.SyListIndexError):
            path.append(value.index)
            type_, value, frame = value.exc_info
        self._path = path

        fs_encoding = sys.getfilesystemencoding()

        def decode_binary(line):
            if isinstance(line, bytes):
                return line.decode(fs_encoding)
            return line

        if type_ is None:
            self._type = u''
        else:
            self._type = type_.__name__
        self._string = str(value)
        self._trace = []
        self._node_error = issubclass(type_, exceptions.SyNodeError)
        if self._node_error:
            self._details = value.help_text
            try:
                node_error_dict = value.to_dict()
                # Ensure serializable
                json.dumps(node_error_dict)
                self._node_error_dict = node_error_dict
            except Exception:
                pass
        else:
            trace_lines = []
            for line in traceback.format_exception(type_, value, frame):
                line = decode_binary(line)
                trace_lines.append(line)

            self._details = limit_traceback(trace_lines, limit_filename)

            while frame:
                self._trace.append(self._get_trace_step(
                    frame.tb_frame.f_code.co_name,
                    frame.tb_frame.f_lineno,
                    decode_binary(frame.tb_frame.f_code.co_filename)))
                frame = frame.tb_next

    def __str__(self):
        if self.is_raised():
            return self._details
        else:
            return ''

    def to_dict(self):
        return {
            'type': str(self._type),
            'string': str(self._string),
            'node_error': self._node_error,
            'node_error_dict': self._node_error_dict,
            'trace': [(f.function, f.line, f.filename) for f in self._trace],
            'details': str(self._details),
            'path': '; '.join([str(p) for p in self._path])}

    def is_raised(self):
        return self._type is not None and self._type != ''

    @property
    def type(self):
        return self._type

    @property
    def string(self):
        return self._string

    @property
    def node_error(self):
        return self._node_error

    @property
    def node_error_instance(self) -> Optional[exceptions.SyNodeError]:
        error = None
        if self._node_error and self._node_error_dict:
            try:
                error = exceptions._internal_node_error_from_dict(
                    self._node_error_dict)
            except Exception:
                pass
        return error

    @property
    def details(self):
        return str(self._details)

    @property
    def path(self):
        return self._path


class NodeResult(object):
    """
    Wrapper for node execution/validation/configuration outputs.
    """

    def __init__(self):
        super(NodeResult, self).__init__()
        self._stderr = u''
        self._stdout = u''
        self._exception = ExceptionInformation()
        self._valid = True
        self._output = None
        self._exitcode = None
        self._times = {'started': datetime.datetime.now()}
        self.stdout_limit = None
        self.stderr_limit = None
        self._stdout_clean = False
        self._stderr_clean = False
        self._child_results = []
        self.limit_footer = None
        self._id = str(uuid.uuid4())

    @classmethod
    def from_dict(cls, d):
        instance = cls()
        if isinstance(d, int):
            instance._stdout = ''
            instance._stderr = 'Worker exited with code {}'.format(d)
            instance._exception = ExceptionInformation()
            instance._valid = False
            instance._output = False
            instance._exitcode = d
            instance._times = {}
            instance._child_results = []
        else:
            instance._stdout = d['stdout']
            instance._stderr = d['stderr']
            instance._exception = ExceptionInformation.from_dict(
                d['exception'])
            instance._valid = d['valid']
            instance._output = d['output']
            instance._times = {k: datetime.datetime.fromisoformat(v)
                               for k, v in d['times'].items()}
            instance._exitcode = d['exitcode']
            instance._child_results = [(node_id, NodeResult.from_dict(c))
                                       for node_id, c in d['child_results']]
            instance._id = d['id']

        return instance

    def update(self, other):
        if 'stdout' in other:
            self._stdout = other['stdout']
        if 'stderr' in other:
            self._stderr = other['stderr']
        if 'exception' in other:
            self._exception = ExceptionInformation.from_dict(
                other['exception'])
        if 'valid' in other:
            self._valid = other['valid']
        if 'output' in other:
            self._output = other['output']
        if 'times' in other:
            self._times = {k: datetime.datetime.fromisoformat(v)
                           for k, v in other['times'].items()}
        if 'exitcode' in other:
            self._exitcode = other['exitcode']

        if 'child_results' in other:
            self._child_results = other['child_results']

        if 'id' in other:
            self._id = other['id']

    def _limit(self, data, n):
        res = data
        if n:
            len_data = len(data)
            if len_data > n:
                footer = (
                    '\n\n...\nCharacter limit (Preferences -> Advanced): {} '
                    'reached, total characters: {}.'.format(n, len_data))
                if self.limit_footer:
                    footer = '{}\n{}'.format(footer, self.limit_footer)
                res = data[:n] + footer
        return res

    @property
    def stderr(self):
        return str(
            self._limit(self._stderr, self.stderr_limit))

    @stderr.setter
    def stderr(self, value):
        self._stderr = value

    @property
    def stdout(self):
        return str(
            self._limit(self._stdout, self.stdout_limit))

    @stdout.setter
    def stdout(self, value):
        self._stdout = value

    @property
    def exception(self):
        return self._exception

    @exception.setter
    def exception(self, value):
        self._exception = value

    def store_current_exception(self, limit_filename=None):
        self._exception = ExceptionInformation.from_exc_info(
            limit_filename)

    @property
    def output(self):
        if self._output:
            return json.loads(self._output)
        else:
            return None

    @output.setter
    def output(self, value):
        self._output = json.dumps(value)

    def set_done(self):
        self._times['done'] = datetime.datetime.now()

    @property
    def valid(self):
        return self._valid

    @valid.setter
    def valid(self, value):
        self._valid = value

    @property
    def times(self):
        return self._times

    def format_std_output(self):
        output = u''
        if len(self._stdout) > 0:
            output += u'----- stdout: {}\n'.format(self.stdout)

        if len(self._stderr) > 0:
            output += u'----- stderr: {}\n'.format(self.stderr)
        return output

    def to_dict(self):
        return {
            'stdout': self.stdout,
            'stderr': self.stderr,
            'exception': (self._exception.to_dict()
                          if self._exception is not None else None),
            'valid': self._valid,
            'output': self._output,
            'exitcode': self._exitcode,
            'times': {k: v.isoformat() for k, v in self._times.items()},
            'child_results': [(node_id, c.to_dict())
                              for node_id, c in self._child_results],
            # 'child_results': {},
            'id': self._id,
        }

    def __str__(self):
        return json.dumps(self.to_dict(), indent=2)

    def has_exception(self):
        return self._exception.is_raised()

    def has_error(self):
        return self.has_exception() or self._exitcode

    @property
    def status(self):
        return 0 if self.has_error() else 1

    def log_times(self):
        for k, v in sorted(self._times.items(), key=lambda x: x[1]):
            node_perf_logger.debug('{} {}'.format(v.isoformat(), k))

    # TODO(erik): refactor.
    @property
    def stdout_clean(self):
        return self._stdout_clean

    @stdout_clean.setter
    def stdout_clean(self, value):
        self._stdout_clean = value

    @property
    def stderr_clean(self):
        return self._stderr_clean

    @stderr_clean.setter
    def stderr_clean(self, value):
        self._stderr_clean = value

    @property
    def child_results(self):
        """
        Returns
        -------
        list of [uuid, NodeResult]
        """
        return self._child_results

    @child_results.setter
    def child_results(self, value):
        """
        Parameters
        ----------
        value : list of [uuid, NodeResult]
        """
        self._child_results = value

    @property
    def id(self):
        return self._id


def from_dict(dict_):
    return NodeResult.from_dict(dict_)
