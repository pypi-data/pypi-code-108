# Allow use of TA_ env vars instead of HT_
import os

import psutil
from hypertrace import env_var_settings
from traceableai.agent import Agent

env_var_settings.ENV_VAR_PREFIXES.append('TA')

# This will initialize the hypertrace instrumentation
a = Agent()
import hypertrace.agent.autoinstrumentation.sitecustomize # pylint:disable=C0413,W0611,C0411


from traceableai.config.config import Config  # pylint:disable=C0413,C0412

from hypertrace.agent.custom_logger import get_custom_logger  # pylint:disable=C0413,C0412,C0411

config = Config()
logger = get_custom_logger(__name__)

__POST_INIT = False
POST_FORK_SERVERS = ['gunicorn']

original_process = psutil.Process(os.getpid())
args = original_process.cmdline()
for entry in POST_FORK_SERVERS:
    for arg in args:
        if entry in arg:
            __POST_INIT = True
            logger.info('Detected server %s - deferring filter loading until post fork', entry)
            break

if __POST_INIT is not True:
    logger.info("Adding TraceableAI Filter during autoinstrumentation")
    a.add_traceable_filter()
