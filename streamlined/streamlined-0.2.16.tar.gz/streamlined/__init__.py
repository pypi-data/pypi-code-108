import resource
import sys

import uvloop

from .common import (
    ACTION,
    ASYNC_NOOP,
    DEFAULT,
    HANDLERS,
    IDENTITY_FACTORY,
    LEVEL,
    LOGGER,
    MESSAGE,
    NOOP,
    TYPE,
    VALUE,
    SubprocessResult,
    Template,
    TemplateParameter,
    TemplateParameterDefault,
    create_identity_function,
    get_default_handler,
    rewrite_function_parameters,
    run,
    use_basic_logging_config,
)
from .execution import SimpleExecutor
from .middlewares import (
    ACTION,
    ARGPARSE,
    ARGS,
    ARGTYPE,
    ARGUMENT,
    ARGUMENTS,
    CHOICES,
    CLEANUP,
    CONST,
    DEFAULT,
    DEST,
    HELP,
    KWARGS,
    LOG,
    METAVAR,
    NAME,
    NARGS,
    PARALLEL,
    PIPELINE,
    REQUIRED,
    RUNSTAGE,
    RUNSTAGES,
    RUNSTEP,
    RUNSTEPS,
    SCHEDULING,
    SEQUENTIAL,
    SETUP,
    SHELL,
    SKIP,
    STDERR,
    STDIN,
    STDOUT,
    VALIDATOR,
    VALIDATOR_AFTER_STAGE,
    VALIDATOR_BEFORE_STAGE,
    Action,
    Argument,
    Arguments,
    Cleanup,
    Context,
    Log,
    Name,
    Pipeline,
    Runstage,
    Runstages,
    Runstep,
    Runsteps,
    Setup,
    Skip,
    Validator,
)
from .services import NameRef, Scoped, Scoping, ValueRef

resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
sys.setrecursionlimit(10 ** 5)

uvloop.install()
