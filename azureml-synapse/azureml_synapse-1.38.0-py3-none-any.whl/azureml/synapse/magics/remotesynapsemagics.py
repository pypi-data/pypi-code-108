# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module to define RemoteSynapseMagics."""

import json
import os
import random
import time

from IPython.core.magic import magics_class, line_cell_magic, needs_local_scope
from IPython.core.magic_arguments import argument, magic_arguments
from azureml.core import Workspace, Environment
from sparkmagic.livyclientlib.exceptions import handle_expected_exceptions
from sparkmagic.utils.utils import parse_argstring_or_throw

from .synapsemagicsbase import SynapseMagicBase
from .. import consts
from .. import telemetryutils
from .. import utils
from ..synapsecomm import SynapseComm


@magics_class
class RemoteSynapseMagics(SynapseMagicBase):
    """The Synapse magic class."""

    # Both the frontend(Notebook UI) and backend(Livy service) limit one active run at a time
    # so the 1:1 mapping for SynapseMagic, SynapseSession, and SessionTracker is good to track
    # the only active run for the magic.

    def __init__(self, shell):
        """Create the magic."""
        super(RemoteSynapseMagics, self).__init__(shell)

    @magic_arguments()
    @argument("command", type=str, default="", nargs="*", help="Commands to execute.")
    @argument("-s", "--subscription-id", help="Subscription id of your AML workspace.")
    @argument("-r", "--resource-group", help="Resource group name of your AML workspace.")
    @argument("-w", "--workspace-name", help="Name of your AML workspace.")
    @argument("-f", "--config-file", help="The path of workspace config file. "
                                          "Will be ignored when subscription-id, "
                                          "resource-group or workspace-name specified.")
    @argument("-c", "--compute-target", help="Name of AML Synapse pool compute.")
    @argument("--driver-memory", default="28g", help="Memory size of Spark driver, default is 28g.")
    @argument("--driver-cores", type=int, default=4, help="Number of VCores of Spark driver, default is 4.")
    @argument("--executor-memory", default="28g", help="Memory size of Spark executor, default is 28g.")
    @argument("--executor-cores", type=int, default=4, help="Number of VCores of Spark executor, default is 4.")
    @argument("-n", "--num-executors", type=int, default=2, help="Number of Spark executors, default is 2.")
    @argument("-t", "--session-timeout", type=int, default=30,
              help="The number of minutes of session timeout, default is 30.")
    @argument("--start-timeout", type=int, default=None,
              help="The number of timeout in seconds when session is initialized, default is None.")
    @argument("-e", "--environment", help="Name of the environment used for this session.")
    @argument("--environment-version", help="version of the environment, will use latest version if not specified.")
    @needs_local_scope
    @line_cell_magic
    @handle_expected_exceptions
    def synapse(self, line, cell="", local_ns=None):
        """Magic to execute spark remotely against a Synapse Spark pool.

        Sub commands:
            start: Start a Livy session against target AML Synapse compute.
                You can set spark config in the magic body by json format. e.g.

                .. code-block:: python

                    %%synapse start --compute-target synapse_compute
                    {
                        "spark.yarn.appMasterEnv.xxx": "xxx",
                        "spark.executorEnv.xxx": "xxx",
                        "spark.yarn.maxAppAttempts": 1
                    }

            run: Run Spark code against the active session.\
                e.g. `%%synapse` or `%%synapse pyspark` will execute the PySpark code against the active session.\
                e.g. `%%synapse spark` will execute the Scala code against the active session.
            meta: Returns the metadata of the active session.
            stop: Stop the active session.
        """
        args = parse_argstring_or_throw(self.synapse, line)
        subcommand = RemoteSynapseMagics._get_subcommand(args.command)
        # start
        if subcommand == "start":
            if self.active_session is not None:
                self.show_error("There is an active session running, please run '%synapse stop' to stop it first.")
                return

            sparkconf = None
            if cell:
                try:
                    sparkconf = json.loads(cell)
                except Exception as ex:
                    self.show_error("Wrong json format. {}".format(ex))
                    return

            synapse_sub, synapse_rg, synapse_workspace, sparkpool, wslocation = self._get_synapse_endpoint_from_args(
                args)
            if synapse_workspace is None or sparkpool is None:
                return

            properties = self._generate_session_properties(args, sparkconf)
            custom_dimensions = {}
            custom_dimensions['environment'] = properties.get('environment', '')
            custom_dimensions['environmentVersion'] = properties.get('environmentVersion', '')
            telemetryutils.log_activity('azureml.synapse.start', custom_dimensions=custom_dimensions,
                                        logger_name="start", func=self._start_session,
                                        args=(synapse_sub, synapse_rg, synapse_workspace, sparkpool, properties,
                                              wslocation, args.session_timeout, args.start_timeout))
        # stop
        elif subcommand == "stop":
            if self.active_session is None:
                self.show_error("No active session to stop.")
                return
            telemetryutils.log_activity('azureml.synapse.stop', logger_name='stop', func=self._stop_session)
            utils.writeln("Session stopped.")
        # meta
        elif subcommand == "meta":
            if self.active_session is None:
                self.show_error("No active session to show metadata.")
                return
            self.active_session.show_meta()
        # list synapse compute
        elif subcommand == "list":
            workspace = self._get_aml_workspace_from_args(args)
            if workspace is None:
                self.show_error("Can't init AML workspace.")
                return
            print(json.dumps(utils._list_synapse_compute(workspace), indent=4))
        # client
        elif subcommand == "client":
            print(SynapseComm._client_info)
        # telemetry
        elif subcommand == "telemetry":
            result = telemetryutils.default_custom_dimensions if telemetryutils.telemetry_enabled else {}
            print(json.dumps(result, indent=4))
        # run
        elif subcommand == "pyspark" or len(subcommand) == 0:
            self.execute(cell, consts.SESSION_KIND_PYSPARK)
        elif subcommand == "spark" or subcommand == "scala":
            self.execute(cell, consts.SESSION_KIND_SPARK)
        elif subcommand == "?" or subcommand == "help":
            utils.write(self.synapse.__doc__)
        else:
            self.show_error("Wrong command. Please look at the usage" + self.synapse.__doc__)

    def _get_synapse_endpoint_from_args(self, args):
        assert args is not None

        if args.compute_target is None:
            self.show_error("Missing compute target name argument.")
            return None, None, None, None, None

        workspace = self._get_aml_workspace_from_args(args)
        if workspace is None:
            self.show_error("Can't init AML workspace.")
            return None, None, None, None, None

        try:
            compute = utils.get_compute(workspace, args.compute_target)
        except Exception as ex:
            self.show_error("Can't find compute target: {}.".format(args.compute_target))
            self.show_error(ex)
            return None, None, None, None, None

        if not utils.is_synapse_compute(compute) or compute.get("resourceId") is None:
            self.show_error("Compute target {} is not a valid Synapse compute.".format(args.compute_target))
            return None, None, None, None, None

        resource_id = compute.get("resourceId")
        (synapse_sub, synapse_rg, synapse_ws, pool) = utils.resolve_synapse_resource_id(resource_id)
        if synapse_ws is not None and pool is not None:
            telemetryutils.set_compute(synapse_ws, pool, resource_id)
            return synapse_sub, synapse_rg, synapse_ws, pool, workspace.location
        else:
            self.show_error("Wrong attached compute: {}.".format(resource_id))

    def _get_aml_workspace_from_args(self, args):
        assert args is not None
        ws = None
        if args.subscription_id is not None and args.resource_group is not None and args.workspace_name is not None:
            ws = Workspace.get(subscription_id=args.subscription_id,
                               resource_group=args.resource_group,
                               name=args.workspace_name)
        elif args.config_file is not None:
            if os.path.isfile(args.config_file):
                ws = Workspace.from_config(path=args.config_file)
            else:
                self.show_error("Can't find the config file {}.".format(args.config_file))
        else:
            ws = Workspace.from_config()
        telemetryutils.set_workspace(ws)
        return ws

    def _generate_session_properties(self, args, sparkconf):
        assert args is not None
        properties = {
            "kind": consts.SESSION_KIND_PYSPARK,  # default language
            "driverMemory": args.driver_memory,
            "driverCores": args.driver_cores,
            "executorMemory": args.executor_memory,
            "executorCores": args.executor_cores,
            "numExecutors": args.num_executors,
            "startTimeout": args.start_timeout,
            "name": "aml_notebook_{}".format(random.randint(1, 1000000))
        }
        sparkconf = self._add_session_conda_dependencies_to_sparkconf(sparkconf, args)
        if sparkconf:
            properties["conf"] = sparkconf
            properties["environment"] = args.environment
            properties["environmentVersion"] = args.environment_version
        return properties

    def _add_session_conda_dependencies_to_sparkconf(self, sparkconf: dict, args) -> dict:
        if args.environment is None:
            return sparkconf
        utils.writeln("Warning: Only Conda dependencies in the environment will be used, and "
                      "Python dependency specified in environment Conda dependencies is not "
                      "supported in Synapse Spark pool. \nSynapse Spark pool now only supports fixed "
                      "Python version, you can print \"sys.version_info\" in your script to check "
                      "current Python version.")
        ws = self._get_aml_workspace_from_args(args)
        env_name = args.environment
        env_ver = args.environment_version

        wait_time = 2
        max_retries = 2
        retries = 0
        while retries < max_retries:
            try:
                # get environment
                env = Environment.get(ws, env_name, env_ver)
                break
            except Exception:
                retries += 1
                utils.writeln('Retry to get environment has happened in {} times'.format(retries))
                if retries < max_retries:
                    time.sleep(wait_time)
                    continue
                else:
                    env_desc = utils._get_env_desc(env_name, env_ver)
                    utils.writeln('Environment {} is not found in AML workspace {}'.format(env_desc, ws.name))
                    raise Exception('Environment not found!')

        if env.python.conda_dependencies is None:
            raise Exception('Only conda_dependency is supported in environment')
        conda_dependencies = env.python.conda_dependencies.serialize_to_string()
        if sparkconf is None:
            sparkconf = dict()
        sparkconf['spark.synapse.library.python.env'] = conda_dependencies
        return sparkconf

    @staticmethod
    def _get_subcommand(command):
        if command is None:
            cmd = None
        elif isinstance(command, str):
            cmd = command
        elif isinstance(command, list):
            if command:
                cmd = command[0]
            else:
                cmd = ''
        else:
            cmd = 'wrong_command'  # to trigger the help

        return '' if cmd is None or not isinstance(cmd, str) else cmd.lower()


def load_ipython_extension(ipython):
    """Load ipython extension."""
    # this method will be automatically called by ipython kernel during start
    ipython.register_magics(RemoteSynapseMagics)
    SynapseComm.register_comm(ipython)
