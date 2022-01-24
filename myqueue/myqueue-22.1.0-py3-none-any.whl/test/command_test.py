from __future__ import annotations
from myqueue.commands import PythonModule


def test_funny_cli_args(capfd):
    arg = "--opt={...,x={'y':(1,2)}"
    cmd = PythonModule('myqueue.test.mod', [arg])
    cmd.run()
    args = capfd.readouterr().out.splitlines()
    assert args[1] == arg
