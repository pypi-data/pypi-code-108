#
# Copyright (c) 2021 by Delphix. All rights reserved.
#
"""
    Delpix Integration (DXI) module for Self Service Bookmarks
    [create | update | share | unshare | list | delete]
"""

from os.path import basename

from delphixpy.v1_10_2 import exceptions
from delphixpy.v1_10_2.web import selfservice
from delphixpy.v1_10_2.web import vo
from dxi._lib import dlpx_exceptions as dxe
from dxi._lib import dx_logging as log
from dxi._lib import dxi_constants as const
from dxi._lib import get_references as ref
from dxi._lib import run_job
from dxi._lib.dxi_constants import BookmarkOps
from dxi._lib.dxi_constants import DataLayoutType
from dxi._lib.run_async import run_async
from dxi._lib.util import DXIConfigConstantsHelper
from dxi.dxi_tool_base import DXIBase
from tabulate import tabulate


class BookmarkConstants(object):
    """
    Class of common Bookmark Constants
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
    MODULE_NAME = basename(__file__).split(".")[0]
    LIST_HEADER = [
        "Bookmark Name",
        "Bookmark Reference",
        "Branch",
        "Bookmark Type",
        "Dataset Name",
        "Tags",
    ]


class DXIBookmark(DXIBase):
    """
    Delphix Integration class for Bookmark Operations

    This class contains all methods to perform Delphix \
    Self Service Bookmark Operations
    """

    def __init__(
        self,
        engine=BookmarkConstants.ENGINE_ID,
        log_file_path=BookmarkConstants.LOG_FILE_PATH,
        config=BookmarkConstants.CONFIG,
        poll=BookmarkConstants.POLL,
        single_thread=BookmarkConstants.SINGLE_THREAD,
        parallel=BookmarkConstants.PARALLEL,
        action=BookmarkConstants.ACTION,
        module_name=BookmarkConstants.MODULE_NAME,
        debug=False,
    ):
        """
        :param engine: Identifier for the Delphix engine in dxtools.conf
        :type engine: `str`

        :param log_file: Log file for the module
        :type log_file: `str`

        :param config: Location (including filename) of the config file
        :type config: `str`

        :param poll: The number of seconds to wait between job polls
        :type poll: `str`

        :param single_thread: Run as single thread.
                              False - To run as multiple threads
                              True - To run as single thead [default]
        :type single_thread: `str`

        :param parallel: Limit number of jobs to maxjob
        :type parallel: int`

        :param action: Type of the action being performed
        :type config: `str`

        :param module_name: Name of the current module
        :type poll: `str`

        """
        super().__init__(
            parallel=parallel,
            poll=poll,
            config=config,
            log_file_path=log_file_path,
            single_thread=single_thread,
            module_name=module_name,
            engine=engine,
            debug=debug,
        )
        self.action = action
        self.tags = ""
        self.bookmark_name = ""
        self.container_name = ""
        self.template_name = ""
        self.branch_name = ""
        self.description = ""
        self.timestamp = ""
        self.expires = ""
        self.new_bookmark_name = ""

    def list(self, tags=None):
        """
        List all existing Bookmarks
        """
        self.action = BookmarkOps.LIST
        self.tags = tags
        self.bm_list = []
        try:
            log.print_info(f"Running dxi bookmark list.")
            self._execute_operation(self._list_bookmark_helper)
            return self.bm_list
        except Exception:
            return False

    def create(
        self,
        bookmark_name,
        container_name,
        template_name,
        branch_name=None,
        timestamp=None,
        expires=None,
        tags=None,
        description=None,
    ):
        """
        :param bookmark_name:
        :param container_name:
        :param template_name:
        :param branch_name:
        :param timestamp: Timestamp to create the bookmark from
                          Format: %Y-%m-%dT%H:%M:%S
                          Sample: 2021-02-23T00:00:00
        :param expires:
        :param tags:
        :param description:
        :return:
        """
        self.action = BookmarkOps.CREATE
        self.tags = tags
        self.bookmark_name = bookmark_name
        self.container_name = container_name
        self.template_name = template_name
        self.branch_name = branch_name
        self.description = description
        self.timestamp = timestamp
        self.expires = expires
        try:
            log.print_info(f"Running dxi bookmark create.")
            self._execute_operation(self._create_bookmark_helper)
            return True
        except Exception:
            return False

    def share(self, bookmark_name):
        """
        Share a bookmark by name
        """
        self.action = BookmarkOps.SHARE
        self.bookmark_name = bookmark_name
        try:
            log.print_info(f"Running dxi bookmark share.")
            self._execute_operation(self._share_bookmark_helper)
            return True
        except Exception:
            return False

    def unshare(self, bookmark_name):
        """
        Unshare a bookmark by name
        """
        self.action = BookmarkOps.UNSHARE
        self.bookmark_name = bookmark_name
        try:
            log.print_info(f"Running dxi bookmark unshare.")
            self._execute_operation(self._unshare_bookmark_helper)
            return True
        except Exception:
            return False

    def update(
        self,
        bookmark_name,
        tags=None,
        expires=None,
        new_bookmark_name=None,
        description=None,
    ):
        """
        Share a bookmark by name
        """
        self.action = BookmarkOps.UPDATE
        self.bookmark_name = bookmark_name
        self.tags = tags
        self.expires = expires
        self.new_bookmark_name = new_bookmark_name
        self.description = description
        try:
            log.print_info(f"Running dxi bookmark update.")
            self._execute_operation(self._update_bookmark_helper)
            return True
        except Exception:
            return False

    def delete(self, bookmark_name):
        """
        Delete a bookmark by name
        """
        self.action = BookmarkOps.DELETE
        self.bookmark_name = bookmark_name
        try:
            log.print_info(f"Running dxi bookmark delete.")
            self._execute_operation(self._delete_bookmark_helper)
            return True
        except Exception:
            return False

    @run_async
    def _list_bookmark_helper(self, engine_ref, dlpx_obj, single_thread):
        """
        List all bookmarks on a specific engine

        :param engine_ref: Dictionary of engines
        :type engine_ref: `dict`

        :param dlpx_obj: DDP session object
        :type dlpx_obj: `lib.GetSession.GetSession`

        :return: list of bookmarks on the engine
        :rtype: `list`
        """
        dlpx_obj = self._initialize_session()
        self._setup_dlpx_session(dlpx_obj, engine_ref)
        tag_filter = None
        display_list = []
        tag = ""
        try:
            with dlpx_obj.job_mode(self.single_thread):
                bookmark_list = []
                ss_bookmarks = selfservice.bookmark.get_all(
                    dlpx_obj.server_session
                )
                for ss_bookmark in ss_bookmarks:
                    branch_name = ref.find_obj_name(
                        dlpx_obj.server_session,
                        selfservice.branch,
                        ss_bookmark.branch,
                    )
                    data_layout = (
                        ss_bookmark.container_name
                        if ss_bookmark.container_name is not None
                        else ss_bookmark.template_name
                    )
                    if self.tags:
                        tag_filter = [x.strip() for x in self.tags.split(",")]
                    if tag_filter is None:
                        tag = ss_bookmark.tags if ss_bookmark.tags else None
                        if tag:
                            tag = ", ".join(tag for tag in ss_bookmark.tags)
                        display_list.append(
                            [
                                ss_bookmark.name,
                                ss_bookmark.reference,
                                branch_name,
                                ss_bookmark.bookmark_type,
                                data_layout,
                                tag,
                            ]
                        )
                        bookmark_list.append(
                            dict(
                                zip(
                                    BookmarkConstants.LIST_HEADER,
                                    [
                                        ss_bookmark.name,
                                        ss_bookmark.reference,
                                        branch_name,
                                        ss_bookmark.bookmark_type,
                                        data_layout,
                                        tag,
                                    ],
                                )
                            )
                        )
                    elif all(tag in ss_bookmark.tags for tag in tag_filter):
                        display_list.append(
                            [
                                ss_bookmark.name,
                                ss_bookmark.reference,
                                branch_name,
                                ss_bookmark.bookmark_type,
                                data_layout,
                                ",".join(tag for tag in ss_bookmark.tags),
                            ]
                        )
                        bookmark_list.append(
                            dict(
                                zip(
                                    BookmarkConstants.LIST_HEADER,
                                    [
                                        ss_bookmark.name,
                                        ss_bookmark.reference,
                                        branch_name,
                                        ss_bookmark.bookmark_type,
                                        data_layout,
                                        ",".join(tag for tag in ss_bookmark.tags),
                                    ],
                                )
                            )
                        )
                self.bm_list = display_list
                print(
                    tabulate(
                        display_list,
                        headers=BookmarkConstants.LIST_HEADER,
                        tablefmt=const.FORMAT_GITHUB,
                    )
                )
            return bookmark_list
        except (
            dxe.DlpxException,
            exceptions.HttpError,
            exceptions.RequestError,
        ) as err:
            log.print_exception(
                f"ERROR: The bookmarks could not be listed. ERROR: {err}"
            )

    @run_async
    def _create_bookmark_helper(self, engine_ref, dlpx_obj, single_thread):
        """
        Creating a bookmark

        :param engine_ref: Dictionary of engines
        :type engine_ref: `dict`

        :param dlpx_obj: DDP session object
        :type dlpx_obj: `lib.GetSession.GetSession`

        :return: created bookmark reference
        :rtype: `str`
        """
        bookmark_ref = None
        dlpx_obj = self._initialize_session()
        self._setup_dlpx_session(dlpx_obj, engine_ref)

        ss_bookmark_params = vo.JSBookmarkCreateParameters()
        ss_bookmark_params.bookmark = vo.JSBookmark()
        ss_bookmark_params.bookmark.name = self.bookmark_name
        data_layout = (
            self.template_name if self.template_name else self.container_name
        )
        layout_type = (
            DataLayoutType.DATA_TEMPLATE.value
            if self.template_name
            else DataLayoutType.DATA_CONTAINER.value
        )
        engine_addr = dlpx_obj.server_session.address
        try:
            if self.template_name:
                data_layout_obj = ref.find_obj_by_name(
                    dlpx_obj.server_session,
                    selfservice.template,
                    self.template_name,
                )
            elif self.container_name:
                data_layout_obj = ref.find_obj_by_name(
                    dlpx_obj.server_session,
                    selfservice.container,
                    self.container_name,
                )
            else:
                log.print_exception(
                    f"A containername or templatename must "
                    f"be provided to create a bookmark"
                )
                self.failures[0] = True
                raise dxe.DlpxException(
                    f"A container or branch much "
                    f"be provided to create a bookmark"
                )
        except dxe.DlpxObjectNotFound:
            log.print_exception(
                f"Unable to find a container or template on engine"
            )
            self.failures[0] = True
            raise dxe.DlpxObjectNotFound(
                "Unable to find a container or template on engine"
            )

        if self.branch_name:
            for branch_obj in selfservice.branch.get_all(
                dlpx_obj.server_session
            ):
                if (
                    self.branch_name == branch_obj.name
                    and data_layout_obj.reference == branch_obj.data_layout
                ):
                    ss_bookmark_params.bookmark.branch = branch_obj.reference
                    break
            if ss_bookmark_params.bookmark.branch is None:
                log.print_exception(
                    f"{self.branch_name} was not found in the "
                    f"{layout_type}:{data_layout}"
                )
                raise dxe.DlpxException(
                    f"{self.branch_name} was not found in the "
                    f"{layout_type}:{data_layout}"
                )
        elif not self.branch_name:
            try:
                ss_bookmark_params.bookmark.branch = (
                    data_layout_obj.active_branch
                )
            except (
                dxe.DlpxException,
                exceptions.RequestError,
                dxe.DlpxObjectNotFound,
            ) as err:
                log.print_exception(
                    f"Could not find a default branch for "
                    f"{self.data_layout_type}:{self.data_layout_name} "
                    f"on engine: {engine_addr} "
                )
                self.failures[0] = True
                raise err

        if self.tags:
            ss_bookmark_params.bookmark.tags = self.tags.split(",")
        if self.description:
            ss_bookmark_params.bookmark.description = self.description
        if self.expires:
            ss_bookmark_params.bookmark.expiration = ref.convert_timestamp_toiso(  # noqa
                dlpx_obj.server_session, self.expires
            )

        ss_bookmark_params.timeline_point_parameters = (
            vo.JSTimelinePointLatestTimeInput()
        )
        ss_bookmark_params.timeline_point_parameters.source_data_layout = (
            data_layout_obj.reference
        )

        if self.timestamp and self.timestamp.lower() != "latest":
            ss_bookmark_params.timeline_point_parameters = (
                vo.JSTimelinePointTimeInput()
            )
            ss_bookmark_params.timeline_point_parameters.branch = (
                ss_bookmark_params.bookmark.branch
            )
            ss_bookmark_params.timeline_point_parameters.time = ref.convert_timestamp_toiso(  # noqa
                dlpx_obj.server_session, self.timestamp
            )

        try:
            with dlpx_obj.job_mode(self.single_thread):
                bookmark_ref = selfservice.bookmark.create(
                    dlpx_obj.server_session, ss_bookmark_params
                )
                self._add_last_job_to_track(dlpx_obj)
                run_job.track_running_jobs(
                    engine_ref,
                    dlpx_obj,
                    poll=self.poll,
                    failures=self.failures,
                )
            return bookmark_ref
        except (
            dxe.DlpxException,
            exceptions.RequestError,
            exceptions.HttpError,
        ) as err:
            log.print_exception(
                f"The bookmark {self.bookmark_name} was not "
                f"created. ERROR :{err}"
            )
            self.failures[0] = True
        except Exception as err:
            log.print_exception(
                f"The bookmark {self.bookmark_name} was not created.\n"
                f"ERROR :{err}"
            )
            self.failures[0] = True

    @run_async
    def _unshare_bookmark_helper(self, engine_ref, dlpx_obj, single_thread):
        """
        UnShare a bookmark
        :param engine_ref: Dictionary of engines
        :type engine_ref: `dict`

        :param dlpx_obj: DDP session object
        :type dlpx_obj: `lib.GetSession.GetSession`

        """
        dlpx_obj = self._initialize_session()
        self._setup_dlpx_session(dlpx_obj, engine_ref)
        try:
            with dlpx_obj.job_mode(self.single_thread):
                bmk_ref = ref.find_obj_by_name(
                    dlpx_obj.server_session,
                    selfservice.bookmark,
                    self.bookmark_name,
                ).reference

                selfservice.bookmark.unshare(dlpx_obj.server_session, bmk_ref)
                log.print_info(f"Bookmark unshare complete.")
                # self._add_last_job_to_track(dlpx_obj)
                # run_job.track_running_jobs(
                #     engine_ref,
                #     dlpx_obj,
                #     poll=self.poll,
                #     failures=self.failures,
                # )
        except (exceptions.HttpError, exceptions.RequestError) as err:
            log.print_exception(
                f"ERROR: Bookmark {self.bookmark_name} could not be unshared. "
                f"ERR: {err}"
            )
            self.failures[0] = True
            # raise err
        except dxe.DlpxObjectNotFound as err:
            log.print_exception(
                f"ERROR: Bookmark {self.bookmark_name} Not found: {err}"
            )
            self.failures[0] = True
            # raise err
        except Exception as err:
            log.print_exception(
                f"ERROR: Bookmark {self.bookmark_name} could not be unshared. "
                f"ERR: {err}"
            )
            self.failures[0] = True
            # raise err

    @run_async
    def _share_bookmark_helper(self, engine_ref, dlpx_obj, single_thread):
        """
        Share a bookmark

        :param engine_ref: Dictionary of engines
        :type engine_ref: `dict`

        :param dlpx_obj: DDP session object
        :type dlpx_obj: `lib.GetSession.GetSession`
        """
        dlpx_obj = self._initialize_session()
        self._setup_dlpx_session(dlpx_obj, engine_ref)
        try:
            with dlpx_obj.job_mode(self.single_thread):
                bmk_ref = ref.find_obj_by_name(
                    dlpx_obj.server_session,
                    selfservice.bookmark,
                    self.bookmark_name,
                ).reference

                selfservice.bookmark.share(dlpx_obj.server_session, bmk_ref)
                log.print_info(f"Bookmark share complete.")
                # self._add_last_job_to_track(dlpx_obj)
                # run_job.track_running_jobs(
                #     engine_ref,
                #     dlpx_obj,
                #     poll=self.poll,
                #     failures=self.failures,
                # )
        except (exceptions.HttpError, exceptions.RequestError) as err:
            log.print_exception(
                f"ERROR: Bookmark {self.bookmark_name} could not be shared. "
                f"ERR: {err}"
            )
            self.failures[0] = True
        except dxe.DlpxObjectNotFound:
            log.print_exception(
                f"ERROR: Bookmark {self.bookmark_name} Not found"
            )
            self.failures[0] = True
        except Exception as err:
            log.print_exception(
                f"ERROR: Bookmark {self.bookmark_name} could not be shared. "
                f"ERR: {err}"
            )
            self.failures[0] = True

    @run_async
    def _update_bookmark_helper(self, engine_ref, dlpx_obj, single_thread):
        """
        Updates a bookmark
        :param engine_ref: Dictionary of engines
        :type engine_ref: `dict`

        :param dlpx_obj: DDP session object
        :type dlpx_obj: `lib.GetSession.GetSession`
        """
        ss_bookmark_obj = vo.JSBookmark()
        dlpx_obj = self._initialize_session()
        self._setup_dlpx_session(dlpx_obj, engine_ref)
        try:
            with dlpx_obj.job_mode(self.single_thread):
                bmk_ref = ref.find_obj_by_name(
                    dlpx_obj.server_session,
                    selfservice.bookmark,
                    self.bookmark_name,
                ).reference
                if self.tags:
                    ss_bookmark_obj.tags = self.tags.split(",")
                if self.description:
                    ss_bookmark_obj.description = self.description
                if self.new_bookmark_name:
                    ss_bookmark_obj.name = self.new_bookmark_name
                if self.expires:
                    ss_bookmark_obj.expiration = ref.convert_timestamp_toiso(  # noqa
                        dlpx_obj.server_session, self.expires
                    )
                selfservice.bookmark.update(
                    dlpx_obj.server_session, bmk_ref, ss_bookmark_obj
                )
                self._add_last_job_to_track(dlpx_obj)
                run_job.track_running_jobs(
                    engine_ref,
                    dlpx_obj,
                    poll=self.poll,
                    failures=self.failures,
                )
                log.print_info(f"Bookmark update complete.")
        except (exceptions.HttpError, exceptions.RequestError) as err:
            log.print_exception(
                f"ERROR: {self.bookmark_name} could not be updated. "
                f"ERR: {err}"
            )
            self.failures[0] = True
        except dxe.DlpxObjectNotFound:
            log.print_exception(f"ERROR: {self.bookmark_name} Not found")
            self.failures[0] = True
        except Exception as err:
            log.print_exception(
                f"ERROR: {self.bookmark_name} could not be updated. "
                f"ERR: {err}"
            )
            self.failures[0] = True

    @run_async
    def _delete_bookmark_helper(self, engine_ref, dlpx_obj, single_thread):
        """
        Deletes a bookmark
        :param engine_ref: Dictionary of engines
        :type engine_ref: `dict`

        :param dlpx_obj: DDP session object
        :type dlpx_obj: `lib.GetSession.GetSession`
        """
        dlpx_obj = self._initialize_session()
        self._setup_dlpx_session(dlpx_obj, engine_ref)
        try:
            with dlpx_obj.job_mode(self.single_thread):
                bmk_ref = ref.find_obj_by_name(
                    dlpx_obj.server_session,
                    selfservice.bookmark,
                    self.bookmark_name,
                ).reference
                selfservice.bookmark.delete(dlpx_obj.server_session, bmk_ref)
                self._add_last_job_to_track(dlpx_obj)
                run_job.track_running_jobs(
                    engine_ref,
                    dlpx_obj,
                    poll=self.poll,
                    failures=self.failures,
                )
                log.print_info(f"Bookmark delete complete.")
        except (exceptions.HttpError, exceptions.RequestError) as err:
            log.print_exception(
                f"ERROR: {self.bookmark_name} could not be deleted. "
                f"ERR: {err}"
            )
            self.failures[0] = True
        except dxe.DlpxObjectNotFound:
            log.print_exception(f"ERROR: {self.bookmark_name} Not found")
            self.failures[0] = True
        except Exception as err:
            log.print_exception(
                f"ERROR: {self.bookmark_name} could not be deleted. "
                f"ERR: {err}"
            )
            self.failures[0] = True
