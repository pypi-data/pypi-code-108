#
# Copyright (c) 2021 by Delphix. All rights reserved.
#

from delphixpy.v1_10_2 import exceptions
from delphixpy.v1_10_2.web import environment
from delphixpy.v1_10_2.web import host
from delphixpy.v1_10_2.web import vo
from dxi._lib import dlpx_exceptions
from dxi._lib import dx_logging
from dxi._lib import get_references
from dxi._lib import run_job
from dxi._lib.dxi_constants import EnvironmentOps
from dxi._lib.dxi_constants import EnvironmentTypes
from dxi._lib.dxi_constants import HostTypes
from dxi._lib.run_async import run_async
from dxi._lib.util import DXIConfigConstantsHelper
from dxi.dxi_tool_base import DXIBase
from tabulate import tabulate


class EnvironmentConstants(object):
    """
    Define constants for Environment operations
    """

    SINGLE_THREAD = False
    POLL = 20
    CONFIG = DXIConfigConstantsHelper().get_config()
    LOG_FILE_PATH = DXIConfigConstantsHelper().get_logdir()
    ENGINE_ID = "default"
    PARALLEL = 5
    TYPE = None
    ACTION = None
    HOSTIP = None
    MODULE_NAME = __name__
    LIST_HEADER = [
        "Env Name",
        "Env Type",
        "Env IP",
        "Enabled",
        "Env User",
        "ASE DB User",
    ]


class DXIEnvironment(DXIBase):
    """
    Perform an environment operation
    """

    def __init__(
        self,
        engine=EnvironmentConstants.ENGINE_ID,
        log_file_path=EnvironmentConstants.LOG_FILE_PATH,
        config_file=EnvironmentConstants.CONFIG,
        poll=EnvironmentConstants.POLL,
        single_thread=EnvironmentConstants.SINGLE_THREAD,
        parallel=EnvironmentConstants.PARALLEL,
        action=EnvironmentConstants.ACTION,
        module_name=EnvironmentConstants.MODULE_NAME,
    ):
        """
        :param engine: Alt Identifier of Delphix engine in dxtools.conf.
        :type engine: `str`
        :param config: The path to the dxtools.conf file
        :type config: `str`
        :param log_file_path: The path to the logfile you want to use.
        :type log_file_path: `str`
        :param poll: The number of seconds to wait between job polls
        :type poll: `int`
        :param single_thread: Run as a single thread.
                              False if running multiple threads.
        :type single_thread: `bool`
        :param action: Operation to perform on the environment.
                       add | update | delete | enable | disable | refresh
        :type action: `str`
        :param env_name: Name of the environment in Delphix
        :type env_name: `str`
        :param env_type: OS type for the environment being added
                         linux | windows
        :type env_type: `str`
        :param toolkit_dir: Toolkit directory on the envrionment
        :type toolkit_dir: `str`
        :param host_ip: IP Address of the host to add
        :type host_ip: `str`
        :param username: Environment OS username
        :type username: `str`
        :param password: Environment user password
        :type password: `str`
        :param connector_env_name: Name of environment with Windows connector
                                   (If adding a Windows environment)
        :type connector_env_name: `str`
        :param old_host: Old IP Address of the environment to update
        :type old_host: `str`
        :param new_host: New IP Address of the environment to update
        :type new_host_: `str`
        :param ase_db_username: ASE DB user
        :type ase_db_username: `str`
        :param ase_db_username: ASE DB user's password
        :type ase_db_username: `str`
        """
        super().__init__(
            parallel=parallel,
            poll=poll,
            config=config_file,
            log_file_path=log_file_path,
            single_thread=single_thread,
            engine=engine,
            module_name=module_name,
        )
        self.action = action
        # self._validate_input()

    def _validate_input(self):
        if not self.action:
            dx_logging.print_exception(
                f"Invalid action provided."
                f"Select at least one option "
                f"(list | add | updatehost | "
                f"delete | refresh | enable | disable)"
            )
            raise

        if self.action == "add":
            if (
                self.env_name is None
                or self.env_type is None
                or self.host_ip is None
                or self.toolkit_dir is None
                or self.username is None
                or self.password is None
            ):
                dx_logging.print_exception(
                    f"Missing input for environment add operation"
                    f"Required parameters: "
                    f"(envname , envtype , hostip , "
                    f"toolkitdir, username, password )"
                )
                raise
            elif (
                self.env_type == "windows" and self.connector_env_name is None
            ):
                dx_logging.print_exception(
                    f"connector_env_name is reqquired "
                    f"to add a Windows environment"
                )
                raise

        if self.action == "updatehost" and (
            self.old_host is None or self.new_host is None
        ):
            dx_logging.print_exception(
                f"Missing required input for updatehost operation"
                f"Required parameters: "
                f"( oldhost , newhost )"
            )
            raise

    def _environment_execution_helper(self):
        """
        Execution helper for all environment operations
        """
        self.display_choices(self)
        for each in run_job.run_job_mt(
            self.main_workflow,
            self.dx_session_obj,
            self.engine,
            self.single_thread,
        ):
            each.join()
        elapsed_minutes = run_job.time_elapsed(self.time_start)
        dx_logging.print_info(
            f"Environment operation took {elapsed_minutes}"
            f" minutes to complete."
        )

    def list(self):
        """
        List all existing environments
        """
        self.action = EnvironmentOps.LIST
        try:
            self._environment_execution_helper()
            dx_logging.print_debug("End of Execution")
            return self.environment_list
        except Exception as err:
            dx_logging.print_exception(
                f"An Error was encountered during "
                f"environment list operation: {repr(err)}"
            )
            return False

    def add(
        self,
        env_name=None,
        env_type=EnvironmentConstants.TYPE,
        host_ip=EnvironmentConstants.HOSTIP,
        toolkit_dir=None,
        os_user=None,
        os_user_pwd=None,
        connector_env_name=None,
        ase_db_user=None,
        ase_db_user_pwd=None,
    ):
        """
        :param env_name: Name of the environment in Delphix
        :type env_name: `str`
        :param env_type: OS type for the environment being added
                         linux | windows
        :type env_type: `str`
        :param toolkit_dir: Toolkit directory on the envrionment
        :type toolkit_dir: `str`
        :param host_ip: IP Address of the host to add
        :type host_ip: `str`
        :param username: Environment OS username
        :type username: `str`
        :param password: Environment user password
        :type password: `str`
        :param connector_env_name: Name of environment with Windows connector
                                   (If adding a Windows environment)
        :type connector_env_name: `str`
        """
        self.action = EnvironmentOps.ADD
        self.env_name = env_name
        self.env_type = env_type
        self.host_ip = host_ip
        self.toolkit_dir = toolkit_dir
        self.username = os_user
        self.password = os_user_pwd
        self.connector_env_name = connector_env_name
        self.ase_db_username = ase_db_user
        self.ase_db_password = ase_db_user_pwd
        try:
            self._environment_execution_helper()
            dx_logging.print_debug(
                "Adding environment to Delphix Engine complete."
            )
            return True
        except Exception as err:
            dx_logging.print_exception(
                f"An Error was encountered during "
                f"environment add operation: {repr(err)}"
            )
            return False

    def enable(self, env_name=None):
        """
        :param env_name: Name of the environment in Delphix
        :type env_name: `str`
        """
        self.env_name = env_name
        self.action = EnvironmentOps.ENABLE
        try:
            self._environment_execution_helper()
            dx_logging.print_debug("End of Execution")
            return True
        except Exception as err:
            dx_logging.print_exception(
                f"An Error was encountered during "
                f"environment enable operation: {repr(err)}"
            )
            return False

    def disable(self, env_name=None):
        """
        :param env_name: Name of the environment in Delphix
        :type env_name: `str`
        """
        self.env_name = env_name
        self.action = EnvironmentOps.DISABLE
        try:
            self._environment_execution_helper()
            dx_logging.print_debug("End of Execution")
            return True
        except Exception as err:
            dx_logging.print_exception(
                f"An Error was encountered during "
                f"environment disable operation: {repr(err)}"
            )
            return False

    def delete(self, env_name=None):
        """
        :param env_name: Name of the environmentin Delphix
        :type env_name: `str`
        """
        self.env_name = env_name
        self.action = EnvironmentOps.DELETE
        try:
            self._environment_execution_helper()
            dx_logging.print_debug("End of Execution")
            return True
        except Exception as err:
            dx_logging.print_exception(
                f"An Error was encountered during "
                f"environment delete operation: {repr(err)}"
            )
            return False

    def refresh(self, env_name=None):
        """
        :param env_name: Name of the environment in Delphix
        :type env_name: `str`
        """
        self.env_name = env_name
        self.action = EnvironmentOps.REFRESH
        try:
            self._environment_execution_helper()
            dx_logging.print_debug("End of Execution")
            return True
        except Exception as err:
            dx_logging.print_exception(
                f"An Error was encountered during "
                f"environment refresh operation: {repr(err)}"
            )
            return False

    def updatehost(self, old_host=None, new_host=None):
        """
        :param old_host: Old IP Address of the environment to update
        :type old_host: `str`
        :param new_host: New IP Address of the environment to update
        :type new_host_: `str`
        """
        self.old_host = old_host
        self.new_host = new_host
        self.action = EnvironmentOps.UPDATEHOST
        try:
            self._environment_execution_helper()
            dx_logging.print_debug("End of Execution")
            return True
        except Exception as err:
            dx_logging.print_exception(
                f"An Error was encountered during "
                f"environment updatehost operation: {repr(err)}"
            )
            return False

    def _enable_environment(self, dlpx_obj):
        """
        Enable the given host
        :param dlpx_obj: DDP session object
        :type dlpx_obj: lib.GetSession.GetSession object
        :param env_name: Environment name in Delphix
        :type env_name: str
        """
        env_obj = get_references.find_obj_by_name(
            dlpx_obj.server_session, environment, self.env_name
        )
        try:
            environment.enable(dlpx_obj.server_session, env_obj.reference)
            self._add_last_job_to_track(dlpx_obj)
        except (dlpx_exceptions.DlpxException, exceptions.RequestError) as err:
            dx_logging.print_exception(
                f"ERROR: Enabling the host {self.env_name} "
                f"encountered an error: {err}"
            )
            raise err

    def _disable_environment(self, dlpx_obj):
        """
        Disable a Delphix environment
        :param dlpx_obj: DDP session object
        :type dlpx_obj: lib.GetSession.GetSession object
        :param env_name: Environment name in Delphix
        :type env_name: str
        """
        env_obj = get_references.find_obj_by_name(
            dlpx_obj.server_session, environment, self.env_name
        )
        try:
            environment.disable(dlpx_obj.server_session, env_obj.reference)
            self._add_last_job_to_track(dlpx_obj)
        except (dlpx_exceptions.DlpxException, exceptions.RequestError) as err:
            dx_logging.print_exception(
                f"ERROR: Disabling the host {self.env_name}"
                f"encountered an error:{err}"
            )
            raise err

    def _update_host_environment(self, dlpx_obj):
        """
        Update the environment
        :param dlpx_obj: DDP session object
        :type dlpx_obj: lib.GetSession.GetSession object
        :param old_host_address: Original IP address of environment
        :type old_host_address: str
        :param new_host_address: New IP address of the environment
        :type new_host_address: str
        """
        old_host_obj = get_references.find_obj_by_name(
            dlpx_obj.server_session, host, self.old_host
        )
        if old_host_obj.type == HostTypes.WIN.value:
            host_obj = vo.WindowsHost()
        else:
            host_obj = vo.UnixHost()
        host_obj.address = self.new_host
        try:
            host.update(
                dlpx_obj.server_session, old_host_obj.reference, host_obj
            )
            self._add_last_job_to_track(dlpx_obj)
        except (dlpx_exceptions.DlpxException, exceptions.RequestError) as err:
            dx_logging.print_exception(
                f"ERROR: Updating the host {host_obj.name} "
                f"encountered an error:{err}"
            )

    def _list_env(self, dlpx_obj):
        """
        List all environments for the engine
        :param dlpx_obj: DDP session object
        :type dlpx_obj: lib.GetSession.GetSession object
        """
        all_envs = environment.get_all(dlpx_obj.server_session)
        self.environment_list = []
        if not all_envs:
            dx_logging.print_info(
                f"There are no environments on "
                f"engine:{dlpx_obj.server_session.address}"
            )
            return
        env_host = ""
        ase_params = ""
        print_list = []
        env_list = []
        for env in all_envs:
            env_user = get_references.find_obj_name(
                dlpx_obj.server_session, environment.user, env.primary_user
            )
            try:
                env_host = get_references.find_obj_name(
                    dlpx_obj.server_session, host, env.host
                )
            except AttributeError:
                pass
            try:
                if hasattr(env, "env.ase_host_environment_parameters"):
                    if isinstance(
                        env.env.ase_host_environment_parameters,
                        vo.ASEHostEnvironmentParameters,
                    ):
                        ase_params = (
                            env.env.ase_host_environment_parameters.db_user
                        )
            except Exception:
                dx_logging.print_exception(
                    "Exception retrieving ASE env info."
                )
            print_list.append(
                [
                    env.name,
                    env.type,
                    env_host,
                    env.enabled,
                    env_user,
                    ase_params,
                ]
            )
            env_list.append(
                dict(
                    zip(
                        EnvironmentConstants.LIST_HEADER,
                        [
                            env.name,
                            env_user,
                            env_host,
                            env.enabled,
                            env_user,
                            ase_params,
                        ],
                    )
                )
            )
        print(
            tabulate(
                print_list,
                headers=EnvironmentConstants.LIST_HEADER,
                tablefmt="grid",
            )
        )
        self.environment_list = env_list
        return env_list

    def _delete_env(self, dlpx_obj):
        """
        Deletes an environment
        :param dlpx_obj: DDP session object
        :type dlpx_obj: lib.GetSession.GetSession object
        :param env_name: Name of the environment to delete
        :type env_name: str
        """
        env_obj = get_references.find_obj_by_name(
            dlpx_obj.server_session, environment, self.env_name
        )
        if env_obj:
            environment.delete(dlpx_obj.server_session, env_obj.reference)
            self._add_last_job_to_track(dlpx_obj)
        elif env_obj is None:
            dlpx_exceptions.DlpxObjectNotFound(
                f"Environment was not found: {self.env_name}"
            )

    def _refresh_env(self, dlpx_obj):
        """
        Refresh the environment
        :param dlpx_obj: DDP session object
        :type dlpx_obj: lib.GetSession.GetSession object
        :parm env_name: Name of the environment to refresh
        :type env_name: str
        """
        if self.env_name == "all":
            env_list = get_references.find_all_objects(
                dlpx_obj.server_session, environment
            )
            for env_obj in env_list:
                try:
                    environment.refresh(
                        dlpx_obj.server_session, env_obj.reference
                    )
                    if dlpx_obj.server_session.last_job:
                        dlpx_obj.jobs[dlpx_obj.server_session.address].append(
                            dlpx_obj.server_session.last_job
                        )
                except (
                    dlpx_exceptions.DlpxException,
                    exceptions.RequestError,
                ) as err:
                    dlpx_exceptions.DlpxException(
                        f"Encountered an error while "
                        f"refreshing {self.env_name}: {err}"
                    )
        else:
            try:
                env_obj = get_references.find_obj_by_name(
                    dlpx_obj.server_session, environment, self.env_name
                )
                environment.refresh(dlpx_obj.server_session, env_obj.reference)
                self._add_last_job_to_track(dlpx_obj)
            except (
                dlpx_exceptions.DlpxException,
                exceptions.RequestError,
            ) as err:
                dx_logging.print_exception(
                    f"Refreshing {self.env_name} encountered an error:{err}"
                )
                raise dlpx_exceptions.DlpxException(
                    f"Refreshing {self.env_name} encountered an error:\n{err}"
                )

    def _add_linux_env(self, dlpx_obj):
        """
        Add a Linux environment.
        :param dlpx_obj: DDP session object
        :type dlpx_obj: lib.GetSession.GetSession object
        """
        env_params_obj = vo.HostEnvironmentCreateParameters()
        env_params_obj.host_environment = vo.UnixHostEnvironment()
        env_params_obj.host_parameters = vo.UnixHostCreateParameters()
        env_params_obj.host_parameters.host = vo.UnixHost()
        env_params_obj.host_environment.name = self.env_name
        env_params_obj.host_parameters.host.address = self.host_ip
        env_params_obj.host_parameters.name = self.env_name
        env_params_obj.host_parameters.host.toolkit_path = self.toolkit_dir
        # setting user credentials
        env_params_obj.primary_user = vo.EnvironmentUser()
        env_params_obj.primary_user.name = self.username

        if self.password is None:
            env_params_obj.primary_user.credential = vo.SystemKeyCredential()
        else:
            env_params_obj.primary_user.credential = vo.PasswordCredential()
            env_params_obj.primary_user.credential.password = self.password
        if self.ase_db_username:
            env_params_obj.host_environment.ase_host_environment_parameters = (  # noqa
                vo.ASEHostEnvironmentParameters()
            )
            env_params_obj.host_environment.ase_host_environment_parameters.db_user = (  # noqa
                self.ase_db_username
            )
            env_params_obj.host_environment.ase_host_environment_parameters.credentials = (  # noqa
                vo.PasswordCredential()
            )
            env_params_obj.host_environment.ase_host_environment_parameters.credentials.password = (  # noqa
                self.ase_db_password
            )
        try:
            environment.create(dlpx_obj.server_session, env_params_obj)
            self._add_last_job_to_track(dlpx_obj)
        except (
            dlpx_exceptions.DlpxException,
            exceptions.RequestError,
            exceptions.HttpError,
        ) as err:
            raise dlpx_exceptions.DlpxException(
                f"ERROR: Encountered an exception while adding the "
                f"environment:{err}"
            )
        except exceptions.JobError as err:
            raise dlpx_exceptions.DlpxException(
                f"JobError while creating environment:{err}"
            ) from err

    def _add_windows_env(self, dlpx_obj):
        """
        Create a Windows environment.
        :param dlpx_obj: DDP session object
        :type dlpx_obj: lib.GetSession.GetSession object
        """
        env_params_obj = vo.HostEnvironmentCreateParameters()
        env_params_obj.primary_user = vo.EnvironmentUser()
        env_params_obj.primary_user.name = self.username
        env_params_obj.primary_user.credential = vo.PasswordCredential()
        env_params_obj.primary_user.credential.password = self.password
        env_params_obj.host_parameters = vo.WindowsHostCreateParameters()
        env_params_obj.host_parameters.host = vo.WindowsHost()
        env_params_obj.host_parameters.host.address = self.host_ip
        env_params_obj.host_parameters.host.connector_port = 9100
        env_params_obj.host_environment = vo.WindowsHostEnvironment()
        env_params_obj.host_environment.name = self.env_name
        env_obj = None
        if self.connector_env_name:
            env_obj = get_references.find_obj_by_name(
                dlpx_obj.server_session, environment, self.connector_env_name
            )
        if env_obj:
            env_params_obj.host_environment.proxy = env_obj.host
        elif self.connector_env_name is not None and env_obj is None:
            raise dlpx_exceptions.DlpxObjectNotFound(
                f"Environment:{self.connector_env_name} "
                f"was not found on the Engine"
            )
        try:
            environment.create(dlpx_obj.server_session, env_params_obj)
            self._add_last_job_to_track(dlpx_obj)
        except (
            dlpx_exceptions.DlpxException,
            exceptions.RequestError,
            exceptions.HttpError,
        ) as err:
            raise dlpx_exceptions.DlpxException(
                f"ERROR: Encountered an exception while adding the "
                f"environment: {err}"
            )

    @run_async
    def main_workflow(self, engine, dlpx_obj, single_thread):
        """
        This function is where we create our main workflow.
        Use the @run_async decorator to run this function asynchronously.
        The @run_async to run against multiple Delphix Engine
        simultaneously
        :param engine: Dictionary of engines
        :type engine: dictionary
        :param dlpx_obj: DDP session object
        :type dlpx_obj: lib.GetSession.GetSession object
        :param single_thread: True - run single threaded,
                              False - run multi-thread
        :type single_thread: bool
        """
        dlpx_obj = self._initialize_session()
        try:
            dlpx_obj.dlpx_session(
                engine["ip_address"],
                engine["username"],
                engine["password"],
                engine["use_https"],
            )
        except dlpx_exceptions.DlpxException as err:
            dx_logging.print_exception(
                f"ERROR: dx_environment encountered an error "
                f'authenticating to {engine["hostname"]}: {err}'
            )
        try:
            with dlpx_obj.job_mode(single_thread):
                if self.action == EnvironmentOps.LIST:
                    env_list = self._list_env(dlpx_obj)
                    return env_list
                elif self.action == EnvironmentOps.ADD:
                    if self.env_type.lower() == EnvironmentTypes.WIN.value:
                        self._add_windows_env(dlpx_obj)
                    else:
                        self._add_linux_env(dlpx_obj)
                elif self.action == EnvironmentOps.ENABLE:
                    self._enable_environment(dlpx_obj)
                elif self.action == EnvironmentOps.DISABLE:
                    self._disable_environment(dlpx_obj)
                elif self.action == EnvironmentOps.DELETE:
                    self._delete_env(dlpx_obj)
                elif self.action == EnvironmentOps.REFRESH:
                    self._refresh_env(dlpx_obj)
                elif self.action == EnvironmentOps.UPDATEHOST:
                    self._update_host_environment(dlpx_obj)
                run_job.track_running_jobs(
                    engine, dlpx_obj, poll=self.poll, failures=self.failures
                )
        except (
            dlpx_exceptions.DlpxException,
            exceptions.RequestError,
            exceptions.JobError,
            exceptions.HttpError,
            Exception,
        ) as err:
            dx_logging.print_exception(
                f"Error in dx_environment on engine:"
                f'{engine["hostname"]}: Error Message: {err}'
            )
            self.failures[0] = True
