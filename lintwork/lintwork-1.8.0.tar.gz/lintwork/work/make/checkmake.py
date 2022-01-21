# -*- coding: utf-8 -*-

import os
import pathlib
import subprocess

from lintwork.work.abstract import WorkAbstract
from lintwork.proto.proto import Format, Type

LINE_SEP = "\\n"

LINT_LEN_MIN = 4
LINT_SEP = ":"


class CheckmakeException(Exception):
    def __init__(self, info):
        super().__init__(self)
        self._info = info

    def __str__(self):
        return self._info


class Checkmake(WorkAbstract):
    def __init__(self, config):
        if config is None:
            config = []
        super().__init__(config)

    def _execution(self, project):
        return self._lint(project)

    def _parse(self, name, data):
        buf = []
        for item in data.strip(LINE_SEP).split(LINE_SEP):
            b = item.strip().split(LINT_SEP)
            if len(b) < LINT_LEN_MIN:
                continue
            buf.append(
                {
                    Format.FILE: name,
                    Format.LINE: int(b[1].strip()),
                    Format.TYPE: Type.ERROR,
                    Format.DETAILS: " ".join(b[3:]).strip(),
                }
            )
        return buf

    def _popen(self, cmd, stdin=None):
        return subprocess.Popen(
            cmd, stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

    def _lint(self, project):
        def _helper(project, name):
            cmd = ["checkmake"]
            cmd.extend(self._config)
            cmd.extend([name])
            with self._popen(cmd) as proc:
                out, err = proc.communicate()
                if proc.returncode == 0:
                    return []
            return self._parse(
                str(name).lstrip(project),
                out.strip().decode("utf-8").replace(project + os.path.sep, ""),
            )

        buf = []
        for item in pathlib.Path(project).glob("**/*"):
            if item.is_file():
                b = _helper(project, item)
                if len(b) != 0:
                    buf.extend(b)
        return buf
