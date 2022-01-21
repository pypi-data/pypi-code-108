#!/usr/bin/env python
"""
Waiting for a port

"""


import os, sys
from functools import partial
import importlib
from devapp.app import app, do, run_app, system
from devapp.tools import (
    FLG,
    project,
    exists,
    repl_dollar_var_with_env_val,
    now,
    wait_for_port,
)


class Flags:
    autoshort = ''

    class port:
        d = '$http_port'

    class host:
        d = '127.0.0.1'

    class timeout:
        d = 5


# ------------------------------------------------------------------------- end actions
def run():
    t0 = now()
    port = int(repl_dollar_var_with_env_val(FLG.port))
    host = repl_dollar_var_with_env_val(FLG.host)
    timeout = float(FLG.timeout)
    if not do(wait_for_port, port, host, timeout):
        app.die('Timeout')
    app.info('Port available', port=FLG.port, millis=now() - t0)


main = partial(run_app, run, flags=Flags)
