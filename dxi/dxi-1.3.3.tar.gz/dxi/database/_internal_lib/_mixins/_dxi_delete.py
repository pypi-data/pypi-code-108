#
# Copyright (c) 2021 by Delphix. All rights reserved.
#
"""
Examples:
  dx_delete_vdb.py --vdb aseTest
  dx_delete_vdb.py --vdb aseTest --engine myengine
  --single_thread False --force
"""

from os.path import basename

from delphixpy.v1_10_2 import exceptions
from delphixpy.v1_10_2.web import database
from delphixpy.v1_10_2.web import vo
from dxi._lib import dlpx_exceptions
from dxi._lib import dx_logging
from dxi._lib import get_references
from dxi._lib import run_job
from dxi._lib.run_async import run_async


class _DeleteMixin(object):
    """
    Deletes a VDB or a list of VDBs from an engine
    """

    def _delete_validate_input(self):
        dx_logging.print_debug("Validating inputs for delete option")

        if not self.name:
            dx_logging.print_exception(
                "Please provide the name of an object to delete. "
                "To provide a list of objects, separate them with colons.\n"
                "Eg  name1:name2"
            )
            raise Exception("Please provide the name of an object to delete.")
        if self.db_type.lower() not in ["vdb", "dsource"]:
            raise Exception('Valid dataset types are: "dSource|VDB')

    def _delete_database_helper(self, dlpx_obj):
        """
        :param datasets: List containing datasets to delete
        :type datasets: `list`
        """
        datasets = self.name.split(":")
        for dataset in datasets:
            try:
                container_obj = get_references.find_obj_by_name(
                    dlpx_obj.server_session, database, dataset
                )
                # Check to make sure our container object has a reference
                source_obj = get_references.find_source_by_db_name(
                    dlpx_obj.server_session, dataset
                )
            except Exception as err:
                dx_logging.print_exception(
                    f"Unable to find a reference for {dataset} on "
                    f"engine {dlpx_obj.server_session.address}: {err}"
                )
                container_obj = None
            if container_obj.reference:
                if self.db_type != "vdb" or source_obj.virtual is not True:
                    dx_logging.print_exception(
                        f"Error : {dataset} is not a virtual object."
                    )
                    raise dlpx_exceptions.DlpxException(
                        f"Error : {dataset} is not a virtual object. "
                    )
                elif self.db_type == "dsource" and (
                    source_obj.linked is True or source_obj.staging is True
                ):
                    dx_logging.print_warning(
                        f"DELETING {dataset} THAT "
                        f"IS EITHER A SOURCE OR STAGING DATASET."
                    )
                elif self.db_type not in ["vdb", "dsource"]:
                    dx_logging.print_exception(
                        f"Error : {dataset} is not the "
                        f"provided type: {self.db_type}"
                    )
                    raise dlpx_exceptions.DlpxException(
                        f"Error : {dataset} is not the "
                        f"provided type: {self.db_type}"
                    )
                dx_logging.print_debug(
                    f"Deleting {dataset} on engine "
                    f"{dlpx_obj.server_session.address}"
                )
                delete_params = None
                if self.force and str(container_obj.reference).startswith(
                    "MSSQL"
                ):
                    delete_params = vo.DeleteParameters()
                    delete_params.force = True
                try:
                    dx_logging.print_debug(f"Deleting dataset : {dataset}")
                    database.delete(
                        dlpx_obj.server_session,
                        container_obj.reference,
                        delete_params,
                    )
                    self._add_last_job_to_track(dlpx_obj)
                except (
                    dlpx_exceptions.DlpxException,
                    exceptions.RequestError,
                    exceptions.HttpError,
                ) as err:
                    raise dlpx_exceptions.DlpxException(f"{err}")

    @run_async
    def _delete_main_workflow(self, engine, dlpx_obj, single_thread):
        """
        This function is where we create our main workflow.
        Use the @run_async decorator to run asynchronously.
        The @run_async decorator allows us to run
        against multiple Delphix Engines simultaneously
        :param engine: Dictionary of engines
        :type engine: dictionary
        :param dlpx_obj: DDP session object
        :type dlpx_obj: lib.GetSession.GetSession object
        :param single_thread:
            True - run single threaded,
            False - run multi-thread
        :type single_thread: bool
        """
        self._delete_validate_input()
        dlpx_obj = self._initialize_session()
        self._setup_dlpx_session(dlpx_obj, engine)
        try:
            with dlpx_obj.job_mode(single_thread):
                self._delete_database_helper(dlpx_obj)
                run_job.track_running_jobs(
                    engine, dlpx_obj, poll=self.poll, failures=self.failures
                )
        except (
            dlpx_exceptions.DlpxException,
            dlpx_exceptions.DlpxObjectNotFound,
            exceptions.RequestError,
            exceptions.JobError,
            exceptions.HttpError,
            Exception,
        ) as err:
            dx_logging.print_exception(
                f"Error in {basename(__file__)} on Delpihx Engine: "
                f'{engine["hostname"]} : {repr(err)}'
            )
            self.failures[0] = True
            # TODO: Add Exception to dictionary
