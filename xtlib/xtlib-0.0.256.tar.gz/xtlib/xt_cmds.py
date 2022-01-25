#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
#
# xt_cmds.py: defines the XT commands, arguments, and options
'''
This module's main() supports the parsing and execution of an XT command.  It is
usually called from xt_run, but can be called directly (as is done in the quicktest and grokserver).
'''
import os
import sys
import time
import logging
import importlib

from xtlib import qfe
from xtlib import utils
from xtlib import errors
from xtlib import constants
from xtlib import file_utils

from xtlib.console import console
from xtlib.helpers.feedbackParts import feedback
from xtlib.impl_shared import ImplShared

logger = logging.getLogger(__name__)

def get_fn_local_config(args):
    '''
    gets path to local config file (specified on cmd line or defaulting to ./xt_config.yaml)
    '''
    # default value
    fn = os.path.join(".", constants.CONFIG_FN)

    # is config file specified by --config option or as a run command with .yaml file script?
    cmd = " ".join(args)
    parts = utils.cmd_split(cmd)
    found_run = False

    for i, part in enumerate(parts):
        # don't change the order of these checks
        if found_run:
            if part.endswith(".yaml"):
                fn = part
            else:
                # is there an XT confile file in the script dir?
                fnx = os.path.join(os.path.dirname(part), constants.CONFIG_FN)
                if os.path.exists(fnx):
                    fn = file_utils.rel_path(fnx, ".")
                    if os.path.dirname(fn):
                        # only print if its not the current directory
                        console.print("using script config file: {}".format(fn))
            break
        
        if part.startswith("--"):
            # process pre-cmd option
            subs = part[2:].split("=", 1)
            option = subs[0]
            if qfe.match(option, "config"):
                if len(subs) == 1:
                    i += 1
                    np = None
                    if i < len(parts):
                        np = parts[i]
                else:
                    np = subs[1]
                if np:
                    if not os.path.exists(np):
                        errors.config_error("--config file not found: {}".format(np))
                    return np

        else:
            if part == "run":
                found_run = True
            else:
                # some other command
                break

    return fn

def main(cmd=None, new_start_time=None, capture_output=False, basic_mode=False, raise_syntax_exception=True):
    '''
    Parse and execute the specified cmd.
    '''
    if new_start_time:
        global xt_start_time
        xt_start_time = new_start_time

    if cmd:
        cmd = cmd.strip()

        if cmd.startswith("xt "):
            cmd = cmd[3:]
        elif cmd == "xt":
            cmd = ""

        args = utils.cmd_split(cmd)

        # remove empty args
        args = [arg for arg in args if arg]
    else:
        # if caller did not supply cmd
        args = sys.argv[1:]
   
    # when executing multiple commands, reset the feedback for each command
    feedback.reset_feedback()

    #console.print("cmd=", cmd, ", args=", args)
    console.diag("in xt_cmds.main")

    #console.print("config=", config)
    fn_local_config = get_fn_local_config(args)

    impl_shared = ImplShared()
    config = impl_shared.init_config(fn_local_config)
    store = impl_shared.store
    basic_mode = not config.get("general", "advanced-mode")

    cmd_providers = config.get("providers", "command")
    impl_dict = {}

    for name, code_path in cmd_providers.items():
        package, class_name = code_path.rsplit(".", 1)
        #console.print("importing package=", package)
        module = importlib.import_module(package)
        impl_class = getattr(module, class_name)

        impl = impl_class(config, store)
        impl_dict[package] = impl

        if name == "help":
            impl.set_basic_mode(basic_mode)

    # this enables QFE to match a function by its module name, to the class instance to process the command
    # impl_dict = {"xtlib.impl_utilities": utilities, "xtlib.impl_storage": storage, 
    #     "xtlib.impl_compute": compute, "xtlib.impl_help": help_impl}

    # this parses args and calls the correct command function with its args and options correctly set.
    # the config object supplies the default value for most options and flags.
    dispatcher = qfe.Dispatcher(impl_dict, config, preprocessor=impl_shared.pre_dispatch_processing)

    if basic_mode:
        # a dict of commands + arg/options to be surfaced (None means use all args/options)
        show_commands = {
            "cancel_all": ["target"],
            "cancel_job": ["job-id"], 
            "cancel_run": ["run-names"],
            "clear_credentials": [],
            "config_cmd": ["which", "create"],
            "create_demo": ["destination", "response"],
            "create_services_template": [],
            "download": ["store-path", "local-path", "share", "workspace", "experiment", "job", "run", "feedback", "snapshot", "show_output"],
            "extract": ["runs", "dest-dir", "browse", "workspace"], 
            "help": ["command", "about", "browse", "version"],
            "help_topics": ["topic", "browse"],
            "list_blobs": ["path"],
            "list_jobs": ["job-list", "experiment", "all", "first", "last", "filter", "sort", "reverse", "status", 
                "available", "tags-all", "tags-any"],
            "list_runs": ["run-list", "job", "experiment", "all", "first", "last", "filter", "sort", "reverse", "status", 
                "available", "tags-all", "tags-any"],
            "monitor": ["name", "workspace"],
            "run": ["script", "script-args", "experiment", "hp-config", "max-runs", "monitor", "nodes", 
                "runs", "search-type", "target", "data-action", "model-action"],
            "upload": ["local-path", "store-path", "share", "workspace", "experiment", "job", "run", "feedback", "show_output"],
            "view_console": ["name", "target", "workspace", "node-index"],
            "view_metrics": ["runs", "metrics"],
            "view_run": ["run-name"]
            }

        dispatcher.show_commands(show_commands)

        #qfe.remove_hidden_commands()
    
    # hide under-development commands
    hide_commands  = ["collect_logs", "start_tensorboard", "stop_tensorboard"]

    # hide internal cmds (for xt development use only)
    hide_commands.append("generate_help")
    dispatcher.hide_commands(hide_commands)

    # expand symbols like $lastjob, $lastrun
    impl_shared.expand_xt_symbols(args)

    # this is the NORMAL outer exeception handling block, but
    # also see the client/server exception handling in xt_run.py
    try:
        text = dispatcher.dispatch(args, capture_output=capture_output, raise_syntax_exception=raise_syntax_exception)  
    except BaseException as ex:
        #console.print("in Exception Handler: utils.show_stack_trace=", utils.show_stack_trace)
        # does user want a stack-trace?
        logger.exception("Error during displatcher.dispatch, args={}".format(args))

        exc_type, exc_value, exc_traceback = sys.exc_info()
        errors.process_exception(exc_type, exc_value, exc_traceback)

    return text

if __name__ == "__main__":
    main()


