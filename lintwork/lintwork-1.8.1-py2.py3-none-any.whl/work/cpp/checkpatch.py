# -*- coding: utf-8 -*-

import os
import pathlib
import subprocess

from lintwork.work.abstract import WorkAbstract
from lintwork.proto.proto import Format, Type

LINT_LEN_MIN = 4
LINT_SEP = ":"
LINT_TYPE = [Type.ERROR, Type.INFO, Type.WARN]


class CheckpatchException(Exception):
    def __init__(self, info):
        super().__init__(self)
        self._info = info

    def __str__(self):
        return self._info


class Checkpatch(WorkAbstract):
    def __init__(self, config):
        if config is None:
            config = []
        super().__init__(config)

    def _execution(self, project):
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
            buf.append(
                {
                    Format.FILE: b[0].strip(),
                    Format.LINE: int(b[1].strip()),
                    Format.TYPE: _helper(b[2].strip()),
                    Format.DETAILS: " ".join(b[3:]).strip(),
                }
            )
        return buf

    def _popen(self, cmd, stdin=None):
        return subprocess.Popen(
            cmd, stdin=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

    def _lint(self, project):
        def _helper(name):
            cmd = ["checkpatch.pl"]
            cmd.extend(self._config)
            cmd.extend(["-f", name])
            with self._popen(cmd) as proc:
                out, err = proc.communicate()
                if proc.returncode == 0:
                    return []
            return self._parse(
                out.strip().decode("utf-8").replace(project + os.path.sep, "")
            )

        buf = []
        for item in pathlib.Path(project).glob("**/*"):
            if item.is_file():
                b = _helper(item)
                if len(b) != 0:
                    buf.extend(b)
        return buf
