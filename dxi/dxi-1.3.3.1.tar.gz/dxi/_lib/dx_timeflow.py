"""
List, create, destroy and refresh Delphix timeflows
"""

import re
import pytz
import sys
from datetime import datetime

from delphixpy.v1_10_2 import exceptions
from delphixpy.v1_10_2 import job_context
from delphixpy.v1_10_2.web import database
from delphixpy.v1_10_2.web import snapshot
from delphixpy.v1_10_2.web import timeflow
from delphixpy.v1_10_2.web import vo
from delphixpy.v1_10_2.web.objects.TimeflowRangeParameters \
    import TimeflowRangeParameters

from . import dlpx_exceptions
from . import dx_logging
from . import get_references
from . import dxi_constants as const

VERSION = "v.0.3.002"


class DxTimeflow:
    """
    Shared methods for timeflows
    :param engine: A Delphix DDP session object
    :type engine: delphixpy.v1_10_2.delphix_engine.DelphixEngine
    """

    def __init__(self, engine):
        super().__init__()
        self._engine = engine

    def get_timeflow_reference(self, db_name):
        """
        :param db_name: The database name to retrieve current_timeflow
        :type db_name: str
        :return: current_timeflow reference for db_name
        """
        db_lst = database.get_all(self._engine)
        for db_obj in db_lst:
            if db_obj.name == db_name:
                return db_obj.current_timeflow
        raise dlpx_exceptions.DlpxException(
            f"Timeflow reference not " f"found for {db_name}."
        )

    def list_timeflows(self):
        """
        Retrieve all timeflows for a given engine
        :return: generator containing
        delphixpy.v1_10_2.web.objects.OracleTimeflow.OracleTimeflow objects
        """
        all_timeflows = timeflow.get_all(self._engine)
        for tf_obj in all_timeflows:
            try:
                tf_obj.name = get_references.find_obj_name(
                    self._engine, database, tf_obj.container
                )
                yield tf_obj
            except TypeError as err:
                raise dlpx_exceptions.DlpxException(
                    f"Listing Timeflows encountered an error:\n{err}"
                )
            except (
                exceptions.RequestError,
                exceptions.JobError,
                exceptions.HttpError,
            ) as err:
                raise dlpx_exceptions.DlpxException(err)

    def create_bookmark(self, bookmark_name, db_name, timestamp=None, location=None):
        """
        Create a timeflow bookmark

        :param bookmark_name: Bookmark's name
        :type bookmark_name: str
        :param db_name: The database name to create the bookmark
        :type bookmark_name: str
        :param timestamp: Timestamp for the bookmark.
        :type timestamp: str Required format is (UTC/Zulu):
                         YYYY-MM-DDTHH:MM:SS.000Z
        :param location: Location which is referenced by the bookmark
        """
        tf_create_params = vo.TimeflowBookmarkCreateParameters()
        tf_ref = self.get_timeflow_reference(db_name)
        if re.search("ORAC", tf_ref, re.IGNORECASE):
            tf_create_params.timeflow_point = vo.OracleTimeflowPoint()
        elif re.search("MSSql", tf_ref, re.IGNORECASE):
            tf_create_params.timeflow_point = vo.MSSqlTimeflowPoint()
        elif re.search("ASE", tf_ref, re.IGNORECASE):
            tf_create_params.timeflow_point = vo.ASETimeflowPoint()
        tf_create_params.name = bookmark_name
        tf_create_params.timeflow_point.timeflow = tf_ref
        if timestamp is not None:
            tf_create_params.timeflow_point.timestamp = timestamp
        else:
            tf_create_params.timeflow_point.location = location
        try:
            timeflow.bookmark.create(self._engine, tf_create_params)
        except exceptions.RequestError as err:
            raise dlpx_exceptions.DlpxException(err.error)
        except (exceptions.JobError, exceptions.HttpError):
            raise dlpx_exceptions.DlpxException(
                f"Fatal exception caught while creating the Timeflow "
                f"Bookmark:\n{sys.exc_info()[0]}\n"
            )

    def delete_bookmark(self, bookmark_name):
        """
        Delete a Timeflow bookmark
        :param bookmark_name: name of the TF bookmark to delete
        :param bookmark_name: str
        """
        tf_bookmark = get_references.find_obj_by_name(
            self._engine, timeflow.bookmark, bookmark_name
        )
        try:
            timeflow.bookmark.bookmark.delete(self._engine, tf_bookmark.reference)
        except exceptions.RequestError as err:
            raise dlpx_exceptions.DlpxException(err.error)
        except (exceptions.JobError, exceptions.HttpError):
            raise dlpx_exceptions.DlpxException(
                f"Fatal exception caught while creating the Timeflow "
                f"Bookmark:\n{sys.exc_info()[0]}\n"
            )

    def list_tf_bookmarks(self):
        """
        Return all Timeflow Bookmarks
        :return: generator containing v1_10_2.web.vo.TimeflowBookmark objects
        """
        all_bookmarks = timeflow.bookmark.get_all(self._engine)
        for tfbm_obj in all_bookmarks:
            try:
                if tfbm_obj.timestamp is None:
                    tfbm_obj.timestamp = None
                else:
                    tfbm_obj.timestamp = get_references.convert_timestamp(
                        self._engine, tfbm_obj.timestamp[:-5]
                    )
                tfbm_obj
            except TypeError:
                raise dlpx_exceptions.DlpxException(
                    f"No timestamp found " f"for {tfbm_obj.name}"
                )
            except exceptions.RequestError as err:
                dlpx_err = err.error
                raise dlpx_exceptions.DlpxException(dlpx_err.action)

    def find_snapshot(self, snap_name):
        """
        Method to find a snapshot by name
        :param snap_name: Name of the snapshot
        :type snap_name: str
        :return: snapshot name
        """
        snapshots = snapshot.get_all(self._engine)
        for snapshot_obj in snapshots:
            if str(snapshot_obj.name).startswith(snap_name):
                return snapshot_obj.reference
            elif str(snapshot_obj.latest_change_point.timestamp).startswith(snap_name):
                return snapshot_obj.reference

    def find_snapshot_object(self, snap_name):
        """
        Method to find a snapshot by name
        :param snap_name: Name of the snapshot
        :type snap_name: str
        :return: snapshot name
        """
        snapshots = snapshot.get_all(self._engine)
        for snapshot_obj in snapshots:
            if str(snapshot_obj.name).startswith(snap_name):
                return snapshot_obj
            elif str(snapshot_obj.latest_change_point.timestamp).startswith(
                    snap_name):
                return snapshot_obj

    def refresh_vdb_tf_bookmark(self, vdb_name, tf_bookmark_name):
        """
        Refreshes a VDB from a Timeflow Bookmark
        :param vdb_name: Name of the VDB
        :type vdb_name: str
        :param tf_bookmark_name: Name of the Timeflow Bookmark
        :type tf_bookmark_name: str
        :return: str reference to the refresh job
        """
        try:
            vdb_obj = get_references.find_obj_by_name(self._engine, database, vdb_name)
            tf_bookmark_obj = get_references.find_obj_by_name(
                self._engine, timeflow.bookmark, tf_bookmark_name
            )
        except StopIteration as err:
            raise dlpx_exceptions.DlpxObjectNotFound(err)
        if "ORACLE" in vdb_obj.reference:
            tf_params = vo.OracleRefreshParameters()
        else:
            tf_params = vo.RefreshParameters()
        tf_params.timeflow_point_parameters = vo.TimeflowPointBookmark()
        tf_params.timeflow_point_parameters.bookmark = tf_bookmark_obj.reference
        try:
            with job_context.asyncly(self._engine):
                database.refresh(self._engine, vdb_obj.reference, tf_params)
                return self._engine.last_job
        except exceptions.RequestError as err:
            raise dlpx_exceptions.DlpxException(err.error.action)
        except (exceptions.JobError, exceptions.HttpError) as err:
            dx_logging.print_exception(
                f"Exception caught during refresh:\n{sys.exc_info()[0]}"
            )
            raise dlpx_exceptions.DlpxException(err.error)


    def find_timeflow_ranges(self, container_ref, timestamp, db_tz):
        """
        Fetches TimeFlow ranges in between
        the specified start and end locations.
        Args:
            container_ref: Reference to VDB or vFile container.
            timestamp: The timestamp to find on datasets timeline.
        Returns:
            timeflow: A timeflow object with the timestamp.
        """
        utc = pytz.UTC
        try:
            db_timeflows = timeflow.get_all(self._engine, container_ref)
            ts_in_utc = get_references.convert_timestamp_dbtz_to_utc(timestamp, db_tz)
            for tf_obj in db_timeflows:
                tf_params = TimeflowRangeParameters()
                tf_range = timeflow.timeflow_ranges(self._engine, tf_obj.reference,tf_params)
                end_point = tf_range[0].end_point.timestamp
                start_point= tf_range[0].start_point.timestamp
                endtime = datetime.strptime(end_point,const.FORMAT_TS_MILLIS)
                endtime = utc.localize(endtime)
                starttime = datetime.strptime(start_point,const.FORMAT_TS_MILLIS)
                starttime = utc.localize(starttime)
                if starttime <= ts_in_utc and endtime >= ts_in_utc:
                    dx_logging.print_debug(f"Match found for the timestamp that was passed.")
                    return tf_obj
            dx_logging.print_debug(f"No match found for the timestamp that was passed.")
        except (
                exceptions.RequestError,
                exceptions.JobError,
                exceptions.HttpError,
        ) as err:
            dx_logging.print_exception(f"Exception in find_timeflow_ranges():{err}")
            raise dlpx_exceptions.DlpxException(err)
        except Exception as err:
            dx_logging.print_exception(f"Exception in find_timeflow_ranges():{err}")
            raise dlpx_exceptions.DlpxException(err)

    def set_timeflow_point(
            self,
            container_obj,
            timestamp_type="SNAPSHOT",
            timestamp="LATEST",
            engine_session_ref=None
    ):
        """
        Returns a TimeflowPointParameters object with a reference to
        the relevant snapthos or timeflow to be used.
        Args:
            container_obj: Reference to the db container
            timestamp_type: Snapshot or Time
            timestamp: Timestamp in %Y-%m-%dT%H:%M:%S.%fZ or LATEST
            engine_session: Reference to engine session.
        Returns:
            timeflow_point_parameters: One of the following types,
            depending on timeflow required
                 TimeflowPointParameters
                 TimeflowPointSnapshot
                 TimeflowPointSemantic
        Raises:
            Exception: Generic Exception.
        """
        timeflow_point_parameters = None
        if timestamp_type.upper() == "SNAPSHOT":
            if timestamp.upper() == "LATEST":
                timeflow_point_parameters = vo.TimeflowPointSemantic()
                timeflow_point_parameters.container = container_obj.reference
                timeflow_point_parameters.location = "LATEST_SNAPSHOT"
            elif timestamp:
                snapshot_obj = self.find_snapshot_object(timestamp)
                if snapshot_obj:
                    timeflow_point_parameters = vo.TimeflowPointSnapshot()
                    timeflow_point_parameters.snapshot = snapshot_obj.reference
                elif snapshot_obj is None:
                    msg = f"A snapshot for the timestamp: {timestamp} " \
                          f"could not be found on database: {container_obj.name}."
                    dx_logging.print_exception(msg)
                    raise dlpx_exceptions.DlpxException(msg)
        elif timestamp_type.upper() == "TIME":
            if timestamp.upper() == "LATEST":
                timeflow_point_parameters = vo.TimeflowPointSemantic()
                timeflow_point_parameters.container = container_obj.reference
                timeflow_point_parameters.location = "LATEST_POINT"
            elif timestamp:
                timeflow_point_parameters = self.create_tfparams_for_timestamp(
                    engine_session_ref,
                    container_obj,
                    timestamp
                )
        return timeflow_point_parameters


    def create_tfparams_for_timestamp(
            self,
            engine_session_ref,
            container_obj,
            timestamp
    ):
        """
        Builds a TimeflowPointParams object from the provided timestamp.
        If exact match to Snapshot is found, then returns a TimeFlowPointSnapshot.
        Else, return a TimeflowPointTimestamp.
        Args:
            db_snapshots_and_tz: Tuple including db timezone and snapshot.
        Returns:
            timeflow_point_parameters: A TimeFlowPointSnapshot or TimeflowPointTimestamp
        Raises:
            Exception: Generic Exception
        """
        func_ref = "DXTimeflow.create_tfparams_for_timestamp()"
        try:
            db_snapshots_and_tz = get_references.find_snapshot_by_timestamp(
                engine_session_ref,
                container_obj.reference,
                timestamp
            )
            if db_snapshots_and_tz is None:
                msg = f"Could not find any snapshots " \
                      f"on database: {container_obj.name}"
                raise Exception(msg)
            db_tz = db_snapshots_and_tz[0]
            snapshots = db_snapshots_and_tz[1]

            # if more than one snapshot, raise error.
            if len(snapshots)>1:
                msg = f"Multiple snapshots were found for timestamp: {timestamp} " \
                      f"on database: {container_obj.name}. Cannot continue the operation."
                raise Exception(msg)
            else:
                if len(snapshots)==1:
                    # checking for an exact match.
                    snap = snapshots[0]
                    last_changetime = snap.latest_change_point.timestamp
                    ts_in_utc = get_references.convert_timestamp_dbtz_to_utc(timestamp, db_tz)
                    last_changetime_utc = get_references.convert_timestamp_dbtz_to_utc(last_changetime, "UTC")
                    if(last_changetime_utc == ts_in_utc):
                        dx_logging.print_debug(f"Found a snapshot:{snap.reference} that "
                                                   f"matches the timestamp: {timestamp}.")
                        timeflow_point_parameters = vo.TimeflowPointSnapshot()
                        timeflow_point_parameters.snapshot = snap.reference
                        return timeflow_point_parameters
                    else:
                        dx_logging.print_debug(f"No snapshot found. "
                                               f"Using the snapshot timeflow")
                        return self.create_tfparams_from_timeflow(
                            container_obj.reference,
                            timestamp,
                            db_tz,
                            snap.timeflow
                        )
                else:
                    dx_logging.print_debug(f"No snapshot found. Looking for timeflow")
                    return self.create_tfparams_from_timeflow(
                        container_obj.reference,
                        timestamp,
                        db_tz
                    )
        except Exception as err:
            dx_logging.print_exception(f"{err}",func_ref)

    def create_tfparams_from_timeflow(
            self,
            container_ref,
            timestamp,
            db_tz,
            timeflow_ref=None
    ):
        """
        Builds a TimeFlowPointTimestamp object from a Timeflow
        Args:
            container_ref, Reference to the vdb or dsource
            ts: Timestamp look for on the timeflow.
            db_tz: Timezone of the DB
        Returns:
            timeflow_point_parameters (TimeflowPointTimestamp)
        Raises:
            Exception: General Exception
        """
        timeflow_point_parameters = vo.TimeflowPointTimestamp()
        if timeflow_ref is not None:
            timeflow_point_parameters.timeflow = timeflow_ref
            ts_in_utc = get_references.convert_timestamp_dbtz_to_utc(timestamp, db_tz)
            timeflow_point_parameters.timestamp = (
                ts_in_utc.isoformat()
            )
        else:
            tf = self.find_timeflow_ranges(
                container_ref,
                timestamp,
                db_tz
            )
            if tf is not None:
                timeflow_point_parameters.timeflow = tf.reference
                ts_in_utc = get_references.convert_timestamp_dbtz_to_utc(timestamp, db_tz)
                timeflow_point_parameters.timestamp = (
                    ts_in_utc.isoformat()
                )
            else:
                msg = f"Unable to find a timeflow for the timestap: {timestamp} " \
                      f"on database. Cannot continue the operation."

                dx_logging.print_exception(msg)
                raise Exception(msg)
        return timeflow_point_parameters