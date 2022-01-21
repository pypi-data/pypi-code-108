# -*- coding: utf-8 -*-

import os
import subprocess

from lintwork.work.abstract import WorkAbstract
from lintwork.proto.proto import Format, Type

LINT_LEN_MIN = 4
LINT_SEP = ":"
LINT_TYPE = [Type.ERROR, Type.INFO, Type.WARN]


class AosplintException(Exception):
    def __init__(self, info):
        super().__init__(self)
        self._info = info

    def __str__(self):
        return self._info


class Aosplint(WorkAbstract):
    def __init__(self, config):
        if config is None:
            config = []
        super().__init__(config)

    def _execution(self, project):
        self._remove(project, "build.gradle")
        return self._lint(project)

    def _parse(self, data):
        def _helper(data):
            buf = ""
            for item in LINT_TYPE:
                if item.lower() in data.lower():
                    buf = item
                    break
            return buf

        buf = []
        for item in data.splitlines():
            b = item.strip().split(LINT_SEP)
            if len(b) < LINT_LEN_MIN:
                continue
            file = b[0].strip()
            ret = _helper(b[1].strip())
            if len(ret) != 0:
                line = 0
                _type = ret
                details = LINT_SEP.join(b[2:]).strip()
            elif type(int(b[1].strip())) == int:
                line = int(b[1].strip())
                _type = _helper(b[2].strip())
                details = LINT_SEP.join(b[3:]).strip()
            else:
                continue
            buf.append(
                {
                    Format.FILE: file,
                    Format.LINE: line,
                    Format.TYPE: _type,
                    Format.DETAILS: details,
                }
            )
        return buf

    def _popen(self, cmd, stdin=None):
        return subprocess.Popen(
            cmd, stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

    def _lint(self, project):
        cmd = ["lint"]
        cmd.extend(self._config)
        cmd.extend([project])
        with self._popen(cmd) as proc:
            out, err = proc.communicate()
            if proc.returncode != 0:
                raise AosplintException(err.strip().decode("utf-8"))
        return self._parse(
            out.strip().decode("utf-8").replace(project + os.path.sep, "")
        )

    def _remove(self, project, file):
        cmd = ["find", project, "-type", "f", "-name", file, "-exec", "rm -f {} \\;"]
        with self._popen(cmd) as proc:
            _, _ = proc.communicate()
            if proc.returncode != 0:
                pass
