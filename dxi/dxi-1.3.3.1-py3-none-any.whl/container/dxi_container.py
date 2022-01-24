#
# Copyright (c) 2021 by Delphix. All rights reserved.
#

from os.path import basename

from delphixpy.v1_10_2.web import database
from delphixpy.v1_10_2.web import selfservice
from delphixpy.v1_10_2.web import user
from delphixpy.v1_10_2.web import vo
from dxi._lib import dx_logging
from dxi._lib import get_references
from dxi._lib import dxi_constants as const
from dxi._lib import run_job
from dxi._lib.dlpx_exceptions import DXIException
from dxi._lib.run_async import run_async
from dxi._lib.util import DXIConfigConstantsHelper
from dxi.dxi_tool_base import DXIBase
from tabulate import tabulate



class DXIContainerConstants(object):
    """
    Define constants for Self Service Container class and CLI usage
    """

    ALL_DBS = False
    SINGLE_THREAD = False
    POLL = 20
    CONFIG = DXIConfigConstantsHelper().get_config()
    LOG_FILE_PATH = DXIConfigConstantsHelper().get_logdir()
    BCK_FILE = None
    USE_BACKUP = False
    CREATE_BACKUP = False
    ENGINE_ID = "default"
    NAME = None
    GROUP = None
    PARALLEL = 5
    LIST_HEADER = [
        "Engine",
        "Container Name",
        "Active Branch",
        "Owner",
        "Reference",
        "Template",
        "Last Updated",
    ]


class DXIContainer(DXIBase):
    """
    Create a snapshot a dSource or VDB
    """

    def __init__(
        self,
        engine=DXIContainerConstants.ENGINE_ID,
        single_thread=DXIContainerConstants.SINGLE_THREAD,
        config=DXIContainerConstants.CONFIG,
        log_file_path=DXIContainerConstants.LOG_FILE_PATH,
        poll=DXIContainerConstants.POLL,
        debug=False,
    ):
        """
        :param engine: An Identifier of Delphix engine in dxtools.conf.
        :type engine: `str`
        :param single_thread: Run as a single thread.
            False if running multiple threads.
        :type single_thread: `bool`
        :param config: The path to the dxtools.conf file
        :type config: `str`
        :param log_file_path: The path to the logfile you want to use.
        :type log_file_path: `str`

        """
        super().__init__(
            config=config,
            log_file_path=log_file_path,
            single_thread=single_thread,
            engine=engine,
            poll=poll,
            module_name=basename(__file__).split(".")[0],
            debug=debug,
        )
        # self.display_choices(self)
        self.container_name = ""
        self.template_name = ""
        self.database_name = ""
        self.keep_vdbs = False
        self.bookmark_name = ""
        self.owner_name = ""

    def list(self):
        """
        List all Self-Service containers.
        Returns:
            container_list: A list of containers on the Delphix Engines.
        Raises:
            Does not raise an exception. If an exception is encountered,
            returns a boolean False.
        """
        self.print_list = []
        self.container_list = []
        try:
            dx_logging.print_info(f"Running dxi container list.")
            self._execute_operation(self.__list_container_helper)
            self._display_list(self.print_list,DXIContainerConstants.LIST_HEADER)
            return self.container_list
        except Exception:
            return False

    @run_async
    def __list_container_helper(self, engine_ref, dlpx_obj, single_thread):
        """
        :param engine_ref: Dictionary of engines
        :type engine_ref: `dict`
        :param dlpx_obj: DDP session object
        :type dlpx_obj: `lib.GetSession.GetSession`
        :param single_thread: True - run single threaded, False -
            run multi-thread
        :type single_thread: `bool`
        :return: Give all containers on a given engine
        :rtype: `list`
        """
        try:
            dlpx_obj = self._initialize_session()
            self._setup_dlpx_session(dlpx_obj, engine_ref)
            with dlpx_obj.job_mode(single_thread):
                ss_containers = selfservice.container.get_all(
                    dlpx_obj.server_session
                )
                dx_logging.print_debug(DXIContainerConstants.LIST_HEADER)
                for ss_container in ss_containers:
                    last_updated = get_references.convert_timestamp(
                        dlpx_obj.server_session, ss_container.last_updated[:-5]
                    )
                    dx_logging.print_debug(
                        f"{ss_container.name}, {ss_container.active_branch}, "
                        f"{ss_container.owner}, {ss_container.reference},"
                        f"{ss_container.template}, {last_updated}"
                    )
                    self.print_list.append(
                        [
                            engine_ref["hostname"],
                            ss_container.name,
                            ss_container.active_branch,
                            ss_container.owner,
                            ss_container.reference,
                            ss_container.template,
                            last_updated,
                        ]
                    )
                    self.container_list.append(
                        dict(
                            zip(
                                DXIContainerConstants.LIST_HEADER,
                                [
                                    engine_ref["hostname"],
                                    ss_container.name,
                                    ss_container.active_branch,
                                    ss_container.owner,
                                    ss_container.reference,
                                    ss_container.template,
                                    last_updated,
                                ],
                            )
                        )
                    )
        except DXIException as err:
            dx_logging.print_exception(err)
            self.failures[0] = True
        except Exception as err:
            dx_logging.print_exception(
                f"ERROR: An error occurred while listing "
                f"Self-Service containers.\n {err}"
            )
            self.failures[0] = True

    def create(self, container_name, template_name, db_name):
        """
        :param container_name: Name of the SS Container
        :type container_name: `str`
        :param template_name:  Name of the JS Template to use for the container
        :type template_name: `str`
        :param db_name: Name of the child database(s) to use for the
                    SS Container
        :type db_name: `str`
        :return: created container reference
        :rtype: `str`
        """
        if not (container_name or template_name or db_name):
            dx_logging.print_exception("Some required parameters are missing.")
            return
        self.container_name = container_name
        self.template_name = template_name
        self.database_name = db_name
        try:
            dx_logging.print_info(f"Running dxi container create")
            self._execute_operation(self.__create_container_helper)
            return True
        except Exception:
            return False

    @run_async
    def __create_container_helper(self, engine_ref, dlpx_obj, single_thread):
        """
        :param engine_ref: Dictionary of engines
        :type engine_ref: `dict`
        :param dlpx_obj: DDP session object
        :type dlpx_obj: `lib.GetSession.GetSession`
        :param single_thread: True - run single threaded, False -
            run multi-thread
        :type single_thread: `bool`
        :return: created container reference
        :rtype: `str`
        """
        try:
            dlpx_obj = self._initialize_session()
            self._setup_dlpx_session(dlpx_obj, engine_ref)
            with dlpx_obj.job_mode(single_thread):
                ss_container_params = (
                    vo.JSDataContainerCreateWithoutRefreshParameters()
                )
                container_ds_lst = []
                for data_set in self.database_name.split(":"):
                    container_ds_lst.append(
                        get_references.build_data_source_params(
                            dlpx_obj, database, data_set
                        )
                    )
                ss_template_ref = get_references.find_obj_by_name(
                    dlpx_obj.server_session,
                    selfservice.template,
                    self.template_name,
                ).reference
                ss_container_params.template = ss_template_ref
                ss_container_params.timeline_point_parameters = (
                    vo.JSTimelinePointLatestTimeInput()
                )
                ss_container_params.timeline_point_parameters.sourceDataLayout = (  # noqa
                    ss_template_ref
                )
                ss_container_params.data_sources = container_ds_lst
                ss_container_params.name = self.container_name
                container_ref = selfservice.container.create(
                    dlpx_obj.server_session, ss_container_params
                )

                self._add_last_job_to_track(dlpx_obj)
                run_job.track_running_jobs(
                    engine_ref,
                    dlpx_obj,
                    poll=self.poll,
                    failures=self.failures,
                )
                return container_ref
        except DXIException as err:
            dx_logging.print_exception(err)
            self.failures[0] = True
        except (Exception, BaseException) as err:
            dx_logging.print_exception(
                f"Container {self.container_name} was not created. "
                f"The error was:\n{str(err)}"
            )
            self.failures[0] = True

    def delete(self, container_name, delete_vdbs=False, keep_vdbs=True):
        """
        :param container_name: Name of the SS Container
        :type container_name: `str`
        :param keep_vdbs:  If set, deleting the container will not
            remove the underlying VDB
        :type keep_vdbs: `str`
        :return: True if execution succeeds, else False
        :rtype: `bool`
        """
        self.container_name = container_name
        self.delete_vdbs = delete_vdbs
        self.keep_vdbs = not(delete_vdbs)
        try:
            dx_logging.print_info(f"Running dxi container delete")
            self._execute_operation(self.__delete_container_helper)
            return True
        except Exception:
            return False

    @run_async
    def __delete_container_helper(self, engine_ref, dlpx_obj, single_thread):
        """
        :param engine_ref: Dictionary of engines
        :type engine_ref: `dict`
        :param dlpx_obj: DDP session object
        :type dlpx_obj: `lib.GetSession.GetSession`
        :param single_thread: True - run single threaded, False -
            run multi-thread
        :type single_thread: `bool`
        :return: True if execution succeeds, else False
        :rtype: `bool`
        """
        try:
            dlpx_obj = self._initialize_session()
            self._setup_dlpx_session(dlpx_obj, engine_ref)
            with dlpx_obj.job_mode(single_thread):
                if self.keep_vdbs:
                    dx_logging.print_debug("VDB will not be deleted")
                    ss_container_params = vo.JSDataContainerDeleteParameters()
                    ss_container_params.delete_data_sources = False
                    selfservice.container.delete(
                        dlpx_obj.server_session,
                        get_references.find_obj_by_name(
                            dlpx_obj.server_session,
                            selfservice.container,
                            self.container_name,
                        ).reference,
                        ss_container_params,
                    )
                else:
                    selfservice.container.delete(
                        dlpx_obj.server_session,
                        get_references.find_obj_by_name(
                            dlpx_obj.server_session,
                            selfservice.container,
                            self.container_name,
                        ).reference,
                    )
                self._add_last_job_to_track(dlpx_obj)
                run_job.track_running_jobs(
                    engine_ref,
                    dlpx_obj,
                    poll=self.poll,
                    failures=self.failures,
                )
        except DXIException as err:
            dx_logging.print_exception(err)
            self.failures[0] = True
        except (Exception, BaseException) as err:
            dx_logging.print_exception(
                f"Container {self.container_name} was not deleted. "
                f"The error was:\n{str(err)}"
            )
            self.failures[0] = True

    def reset(self, container_name):
        """
        Undo the last refresh or restore operation

        :param container_name: Name of the SS Container
        :type container_name: `str`
        :return: True if execution succeeds, else False
        :rtype: `bool`
        """
        self.container_name = container_name
        try:
            dx_logging.print_info(f"Running dxi container reset")
            self._execute_operation(self.__reset_container_helper)
            return True
        except Exception:
            return False

    @run_async
    def __reset_container_helper(self, engine_ref, dlpx_obj, single_thread):
        """
        :param engine_ref: Dictionary of engines
        :type engine_ref: `dict`
        :param dlpx_obj: DDP session object
        :type dlpx_obj: `lib.GetSession.GetSession`
        :param single_thread: True - run single threaded, False -
            run multi-thread
        :type single_thread: `bool`
        :return: True if execution succeeds, else False
        :rtype: `bool`
        """
        try:
            dlpx_obj = self._initialize_session()
            self._setup_dlpx_session(dlpx_obj, engine_ref)
            with dlpx_obj.job_mode(single_thread):
                selfservice.container.reset(
                    dlpx_obj.server_session,
                    get_references.find_obj_by_name(
                        dlpx_obj.server_session,
                        selfservice.container,
                        self.container_name,
                    ).reference,
                )
                self._add_last_job_to_track(dlpx_obj)
                run_job.track_running_jobs(
                    engine_ref,
                    dlpx_obj,
                    poll=self.poll,
                    failures=self.failures,
                )
        except DXIException as err:
            dx_logging.print_exception(err)
            self.failures[0] = True
        except (Exception, BaseException) as err:
            dx_logging.print_exception(
                f"ERROR: SS Container was not reset. "
                f"The error was:\n{str(err)}"
            )
            self.failures[0] = True

    def refresh(self, container_name):
        """
        :param container_name: Name of the SS Container
        :type container_name: `str`
        :return: True if execution succeeds, else False
        :rtype: `bool`
        """
        self.container_name = container_name
        try:
            dx_logging.print_info(f"Running dxi container refresh")
            self._execute_operation(self.__refresh_container_helper)
            return True
        except Exception:
            return False

    @run_async
    def __refresh_container_helper(self, engine_ref, dlpx_obj, single_thread):
        """
        :param engine_ref: Dictionary of engines
        :type engine_ref: `dict`
        :param dlpx_obj: DDP session object
        :type dlpx_obj: `lib.GetSession.GetSession`
        :param single_thread: True - run single threaded, False -
            run multi-thread
        :type single_thread: `bool`
        :return: True if execution succeeds, else False
        :rtype: `bool`
        """
        try:
            dlpx_obj = self._initialize_session()
            self._setup_dlpx_session(dlpx_obj, engine_ref)
            with dlpx_obj.job_mode(single_thread):
                selfservice.container.refresh(
                    dlpx_obj.server_session,
                    get_references.find_obj_by_name(
                        dlpx_obj.server_session,
                        selfservice.container,
                        self.container_name,
                    ).reference,
                )
                self._add_last_job_to_track(dlpx_obj)
                run_job.track_running_jobs(
                    engine_ref,
                    dlpx_obj,
                    poll=self.poll,
                    failures=self.failures,
                )
        except DXIException as err:
            dx_logging.print_exception(err)
            self.failures[0] = True
        except (Exception, BaseException) as err:
            dx_logging.print_exception(
                f"Container {self.container_name} was not refreshed. "
                f"The error was:\n{str(err)}"
            )
            self.failures[0] = True

    def restore(self, container_name, bookmark_name):
        """
        :param container_name: Name of the SS Container
        :type container_name: `str`
        :param bookmark_name:  Name of the JS bookmark to
            restore for the container
        :type bookmark_name: `str`
        :return: True if execution succeeds, else False
        :rtype: `bool`
        """
        self.container_name = container_name
        self.bookmark_name = bookmark_name
        try:
            dx_logging.print_info(f"Running dxi container restore")
            self._execute_operation(self.__restore_container_helper)
            return True
        except Exception:
            return False

    @run_async
    def __restore_container_helper(self, engine_ref, dlpx_obj, single_thread):
        """
        :param engine_ref: Dictionary of engines
        :type engine_ref: `dict`
        :param dlpx_obj: DDP session object
        :type dlpx_obj: `lib.GetSession.GetSession`
        :param single_thread: True - run single threaded, False -
            run multi-thread
        :type single_thread: `bool`
        """
        try:
            dlpx_obj = self._initialize_session()
            self._setup_dlpx_session(dlpx_obj, engine_ref)
            bookmark_params = vo.JSDataContainerRestoreParameters()
            bookmark_params.timeline_point_parameters = (
                vo.JSTimelinePointBookmarkInput()
            )
            bookmark_params.timeline_point_parameters.bookmark = get_references.find_obj_by_name(  # noqa
                dlpx_obj.server_session,
                selfservice.bookmark,
                self.bookmark_name,
            ).reference
            bookmark_params.force_option = False
            with dlpx_obj.job_mode(single_thread):
                selfservice.container.restore(
                    dlpx_obj.server_session,
                    get_references.find_obj_by_name(
                        dlpx_obj.server_session,
                        selfservice.container,
                        self.container_name,
                    ).reference,
                    bookmark_params,
                )
                self._add_last_job_to_track(dlpx_obj)
                run_job.track_running_jobs(
                    engine_ref,
                    dlpx_obj,
                    poll=self.poll,
                    failures=self.failures,
                )
        except DXIException as err:
            dx_logging.print_exception(err)
            self.failures[0] = True
        except (Exception, BaseException) as err:
            dx_logging.print_exception(
                f"The container was not restored:\n{str(err)}"
            )
            self.failures[0] = True

    def connection_info(self, container_name):
        """
        Lists hierarchy of a given container name
        :param container_name: Name of the SS Container
        :type container_name: `str`
        :return: Hierarchy of a given container
        :rtype: `str`
        """
        self.container_name = container_name
        try:
            dx_logging.print_info(f"Running dxi container connection_info")
            self._execute_operation(self.__connection_info_helper)
            return True
        except Exception:
            return False

    @run_async
    def __connection_info_helper(self, engine_ref, dlpx_obj, single_thread):
        """
        :param engine_ref: Dictionary of engines
        :type engine_ref: `dict`
        :param dlpx_obj: DDP session object
        :type dlpx_obj: `lib.GetSession.GetSession`
        :param single_thread: True - run single threaded, False -
            run multi-thread
        :type single_thread: `bool`
        """
        try:
            dlpx_obj = self._initialize_session()
            self._setup_dlpx_session(dlpx_obj, engine_ref)
            headers = ["VDB", "Host", "DB Name", "DB Version", "JDBC"]
            connection_list = []
            with dlpx_obj.job_mode(single_thread):
                layout_ref = get_references.find_obj_by_name(
                    dlpx_obj.server_session,
                    selfservice.container,
                    self.container_name,
                ).reference
                for data_source in selfservice.datasource.get_all(
                    dlpx_obj.server_session, data_layout=layout_ref
                ):
                    data = []
                    db_name = get_references.find_obj_name(
                        dlpx_obj.server_session,
                        database,
                        data_source.container,
                    )

                    data.append(db_name)
                    data.append(data_source.runtime.host)
                    data.append(data_source.runtime.database_name)
                    data.append(data_source.runtime.version)

                    jdbc_str = ""
                    if hasattr(data_source.runtime, "instance_jdbc_string"):
                        jdbc_str = data_source.runtime.instance_jdbc_string
                    # For Oracle
                    elif hasattr(data_source.runtime, "jdbc_strings"):
                        jdbc_str = data_source.runtime.jdbc_strings

                    data.append(jdbc_str)
                    connection_list.append(data)

                self._add_last_job_to_track(dlpx_obj)
                run_job.track_running_jobs(
                    engine_ref,
                    dlpx_obj,
                    poll=self.poll,
                    failures=self.failures,
                )
                print(
                    tabulate(
                        connection_list, headers=headers, tablefmt="fancy_grid"
                    )
                )
        except DXIException as err:
            dx_logging.print_exception(err)
            self.failures[0] = True
        except (Exception, BaseException) as err:
            dx_logging.print_exception(
                f"Failed to find connection info"
                f"{self.container_name}:\n{str(err)}"
            )
            self.failures[0] = True

    def add_owner(self, container_name, owner_name):
        """
        :param container_name: Name of the SS Container
        :type container_name: `str`
        :param owner_name: Name of the JS Owner for the container
        :type owner_name: `str`
        :returns:  True if execution succeeds, else False
        :rtype: `bool`
        """
        self.container_name = container_name
        self.owner_name = owner_name
        try:
            dx_logging.print_info(f"Running dxi container add_owner")
            self._execute_operation(self.__add_owner_helper)
            return True
        except Exception:
            return False

    @run_async
    def __add_owner_helper(self, engine_ref, dlpx_obj, single_thread):
        """
        :param engine_ref: Dictionary of engines
        :type engine_ref: `dict`
        :param dlpx_obj: DDP session object
        :type dlpx_obj: `lib.GetSession.GetSession`
        :param single_thread: True - run single threaded, False -
            run multi-thread
        :type single_thread: `bool`
        """
        try:
            dlpx_obj = self._initialize_session()
            self._setup_dlpx_session(dlpx_obj, engine_ref)
            with dlpx_obj.job_mode(single_thread):
                owner_params = vo.JSDataContainerModifyOwnerParameters()
                owner_params.owner = get_references.find_obj_by_name(
                    dlpx_obj.server_session, user, self.owner_name
                ).reference
                selfservice.container.add_owner(
                    dlpx_obj.server_session,
                    get_references.find_obj_by_name(
                        dlpx_obj.server_session,
                        selfservice.container,
                        self.container_name,
                    ).reference,
                    owner_params,
                )
                self._add_last_job_to_track(dlpx_obj)
                run_job.track_running_jobs(
                    engine_ref,
                    dlpx_obj,
                    poll=self.poll,
                    failures=self.failures,
                )
        except DXIException as err:
            dx_logging.print_exception(err)
            self.failures[0] = True
        except (Exception, BaseException) as err:
            dx_logging.print_exception(
                f"The user was not added from the container "
                f"{self.container_name}:\n{str(err)}"
            )
            self.failures[0] = True

    def remove_owner(self, container_name, owner_name):
        """
        :param container_name: Name of the SS Container
        :type container_name: `str`
        :param owner_name: Name of the JS Owner for the container
        :type owner_name: `str`
        :returns: True if execution succeeds, else False
        :rtype: `bool`
        """
        self.container_name = container_name
        self.owner_name = owner_name
        try:
            dx_logging.print_info(f"Running dxi container remove_owner")
            self._execute_operation(self.__remove_owner_helper)
            return True
        except Exception:
            return False

    @run_async
    def __remove_owner_helper(self, engine_ref, dlpx_obj, single_thread):
        """
        :param engine_ref: Dictionary of engines
        :type engine_ref: `dict`
        :param dlpx_obj: DDP session object
        :type dlpx_obj: `lib.GetSession.GetSession`
        :param single_thread: True - run single threaded, False -
            run multi-thread
        :type single_thread: `bool`
        """
        try:
            dlpx_obj = self._initialize_session()
            self._setup_dlpx_session(dlpx_obj, engine_ref)
            with dlpx_obj.job_mode(single_thread):
                owner_params = vo.JSDataContainerModifyOwnerParameters()
                owner_params.owner = get_references.find_obj_by_name(
                    dlpx_obj.server_session, user, self.owner_name
                ).reference
                container_obj = get_references.find_obj_by_name(
                    dlpx_obj.server_session,
                    selfservice.container,
                    self.container_name,
                )
                selfservice.container.remove_owner(
                    dlpx_obj.server_session,
                    container_obj.reference,
                    owner_params,
                )
                self._add_last_job_to_track(dlpx_obj)
                run_job.track_running_jobs(
                    engine_ref,
                    dlpx_obj,
                    poll=self.poll,
                    failures=self.failures,
                )
        except DXIException as err:
            dx_logging.print_exception(err)
            self.failures[0] = True
        except Exception as err:
            dx_logging.print_exception(
                f"The user was not removed to container "
                f"{self.container_name}. The error was:\n{err}"
            )
            self.failures[0] = True

    def enable(self, container_name):
        """
        :param container_name: Name of the SS Container
        :type container_name: `str`
        :return: True if execution succeeds, else False
        :rtype: `bool`
        """
        self.container_name = container_name
        try:
            dx_logging.print_info(f"Running dxi container enable")
            self._execute_operation(self.__enable_container_helper)
            return True
        except Exception:
            return False

    @run_async
    def __enable_container_helper(self, engine_ref, dlpx_obj, single_thread):
        """
        :param engine_ref: Dictionary of engines
        :type engine_ref: `dict`
        :param dlpx_obj: DDP session object
        :type dlpx_obj: `lib.GetSession.GetSession`
        :param single_thread: True - run single threaded, False -
            run multi-thread
        :type single_thread: `bool`
        :return: True if execution succeeds, else False
        :rtype: `bool`
        """
        try:
            dlpx_obj = self._initialize_session()
            self._setup_dlpx_session(dlpx_obj, engine_ref)
            with dlpx_obj.job_mode(single_thread):
                selfservice.container.enable(
                    dlpx_obj.server_session,
                    get_references.find_obj_by_name(
                        dlpx_obj.server_session,
                        selfservice.container,
                        self.container_name,
                    ).reference
                )
                self._add_last_job_to_track(dlpx_obj)
                run_job.track_running_jobs(
                    engine_ref,
                    dlpx_obj,
                    poll=self.poll,
                    failures=self.failures,
                )
        except DXIException as err:
            dx_logging.print_exception(err)
            self.failures[0] = True
        except (Exception, BaseException) as err:
            dx_logging.print_exception(
                f"Container {self.container_name} was not enabled."
                f"The error was:\n{str(err)}"
            )
            self.failures[0] = True

    def disable(self, container_name):
        """
        :param container_name: Name of the SS Container
        :type container_name: `str`
        :return: True if execution succeeds, else False
        :rtype: `bool`
        """
        self.container_name = container_name
        try:
            dx_logging.print_info(f"Running dxi container disable")
            self._execute_operation(self.__disable_container_helper)
            return True
        except Exception:
            return False

    @run_async
    def __disable_container_helper(self, engine_ref, dlpx_obj, single_thread):
        """
        :param engine_ref: Dictionary of engines
        :type engine_ref: `dict`
        :param dlpx_obj: DDP session object
        :type dlpx_obj: `lib.GetSession.GetSession`
        :param single_thread: True - run single threaded, False -
            run multi-thread
        :type single_thread: `bool`
        :return: True if execution succeeds, else False
        :rtype: `bool`
        """
        try:
            dlpx_obj = self._initialize_session()
            self._setup_dlpx_session(dlpx_obj, engine_ref)
            with dlpx_obj.job_mode(single_thread):
                selfservice.container.disable(
                    dlpx_obj.server_session,
                    get_references.find_obj_by_name(
                        dlpx_obj.server_session,
                        selfservice.container,
                        self.container_name,
                    ).reference
                )
                self._add_last_job_to_track(dlpx_obj)
                run_job.track_running_jobs(
                    engine_ref,
                    dlpx_obj,
                    poll=self.poll,
                    failures=self.failures,
                )
        except DXIException as err:
            dx_logging.print_exception(err)
            self.failures[0] = True
        except (Exception, BaseException) as err:
            dx_logging.print_exception(
                f"Container {self.container_name} was not disabled."
                f"The error was:\n{str(err)}"
            )
            self.failures[0] = True
