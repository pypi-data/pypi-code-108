# -*- coding: utf-8 -*-

import base64
import datetime
import grpc
import json
import os
import pathlib
import shutil

from concurrent import futures
from lintwork.lint.lint_pb2 import LintReply
from lintwork.lint.lint_pb2_grpc import (
    add_LintProtoServicer_to_server,
    LintProtoServicer,
)

LINT_NAME = "lintwork"
MAX_WORKERS = 10


class LintException(Exception):
    def __init__(self, info):
        super().__init__(self)
        self._info = info

    def __str__(self):
        return self._info


class Lint(object):
    def __init__(self, config):
        if config is None:
            raise LintException("config invalid")
        self._config = config

    def _serve(self, routine):
        server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=MAX_WORKERS),
            options=[
                ("grpc.max_receive_message_length", -1),
                ("grpc.max_send_message_length", -1),
            ],
        )
        add_LintProtoServicer_to_server(LintProto(routine), server)
        server.add_insecure_port(self._config.listen_url)
        server.start()
        server.wait_for_termination()

    def run(self, routine):
        self._serve(routine)


class LintProto(LintProtoServicer):
    def __init__(self, routine):
        self._routine = routine

    def _build(self, data):
        def _helper(root, dirs, file, data):
            pathlib.Path(os.path.join(root, dirs)).mkdir(parents=True, exist_ok=True)
            p = pathlib.Path(os.path.join(root, dirs, file))
            with p.open("w", encoding="utf-8") as f:
                f.write(base64.b64decode(data).decode("utf-8"))

        if len(data) == 0:
            return None
        buf = json.loads(data)
        root = os.path.join(
            os.getcwd(),
            LINT_NAME + "-" + datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
        )
        pathlib.Path(root).mkdir(parents=True, exist_ok=True)
        for key, val in buf.items():
            _helper(
                root,
                os.path.dirname(key),
                os.path.basename(key).replace(".base64", ""),
                val,
            )

        return root

    def _clean(self, project):
        if os.path.exists(project):
            shutil.rmtree(project)

    def SendLint(self, request, _):
        if len(request.message) == 0:
            return LintReply(message="")
        project = self._build(request.message.strip())
        if project is None or not os.path.exists(project):
            return LintReply(message="")
        buf = self._routine(project)
        self._clean(project)
        return LintReply(message=json.dumps({LINT_NAME: buf}))
