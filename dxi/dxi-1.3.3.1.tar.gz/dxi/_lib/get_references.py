#
# Copyright (c) 2021 by Delphix. All rights reserved.
#


from datetime import datetime
from pytz import UTC
from pytz import timezone
from dateutil import tz
from delphixpy.v1_10_2 import exceptions
from delphixpy.v1_10_2.web import database
from delphixpy.v1_10_2.web import group
from delphixpy.v1_10_2.web import job
from delphixpy.v1_10_2.web import repository
from delphixpy.v1_10_2.web import source
from delphixpy.v1_10_2.web import sourceconfig
from delphixpy.v1_10_2.web import vo
from delphixpy.v1_10_2.web.service import time
from delphixpy.v1_10_2.web import selfservice
from delphixpy.v1_10_2.web import environment
from delphixpy.v1_10_2.web import snapshot

from . import dlpx_exceptions
from dxi._lib import dx_logging as log
from dxi._lib.util import convert_string_to_datetime


def convert_timestamp(engine, timestamp):
    """
    Convert timezone from Zulu/UTC to the Engine's timezone
    :param engine: A Delphix engine session object
    :type engine: lib.get_session.GetSession object
    :param timestamp: the timstamp in Zulu/UTC to be converted
    :type timestamp: str
    :return: Timestamp converted localtime
    """

    default_tz = tz.gettz("UTC")
    engine_tz = time.time.get(engine)
    try:
        convert_tz = tz.gettz(engine_tz.system_time_zone)
        utc = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")
        utc = utc.replace(tzinfo=default_tz)
        converted_tz = utc.astimezone(convert_tz)
        engine_local_tz = (
            f"{str(converted_tz.date())} "
            f"{str(converted_tz.time())} {str(converted_tz.tzname())}"
        )
        return engine_local_tz
    except TypeError:
        return None


def convert_timestamp_toiso(engine_session, timestamp):
    """
    Convert the provided timestamp to UTC.
    Args:
        engine_session: A Delphix engine session object
        timestamp: Timestamp in Engine's timezone.
    Returns:
        isotime: Iso Format timestamp in UTC Timezone.
    """
    utc_tz = tz.gettz("UTC")
    try:
        engine_time_config = time.time.get(engine_session)
        engine_tz_str = engine_time_config.system_time_zone
        engine_tz = timezone(engine_tz_str)
        ts = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S')
        ts_in_engine_tz = engine_tz.localize(ts)
        ts_in_utc = ts_in_engine_tz.astimezone(utc_tz)
        isotime = ts_in_utc.isoformat()
        return isotime
    except TypeError as err:
        log.print_exception(f"Error while converting the timstamp that was passed.")
        return None

def convert_timestamp_dbtz_to_utc(timestamp, db_tz, iso_format= False):
    """
    Convert timestamp from the DB timezone to UTC.
    Args:
        engine_session: A Delphix engine session object
        timestamp: Timestamp value provided by customer.
        db_tz: The timezone of the DB/Snapshot.
    Returns:
        converted_ts: timestamp in UTC timezone.
    """
    utc_tz = tz.gettz("UTC")
    try:
        if db_tz is None:
            raise Exception("Invalid timezone string.")
        database_tz = timezone(db_tz.split(",")[0])
        if not isinstance(timestamp, datetime):
            timestamp = convert_string_to_datetime(timestamp)
        if timestamp.tzinfo is None or timestamp.tzinfo.utcoffset(timestamp) is None: # noqa
            timestamp = database_tz.localize(timestamp)
        converted_ts = timestamp.astimezone(utc_tz)
        if iso_format:
            converted_ts = converted_ts.isoformat()
        return converted_ts
    except TypeError as err:
        log.print_exception(f"Error while converting the timstamp that was passed: {err}")
        return None
    except Exception as err:
        log.print_exception(f"Error while converting the timstamp that was passed: {err}")
        return None


def get_running_job(engine, object_ref):
    """
    Function to find a running job from the DB target reference.
    :param engine: A Delphix DDP session object
    :type engine: lib.GetSession.GetSession object
    :param object_ref: Reference to the object of the running job
    :type object_ref: str
    :return: reference of the running job(s)
    """
    try:
        return job.get_all(engine, target=object_ref, job_state="RUNNING")[
            0
        ].reference
    except IndexError:
        return None


def find_obj_by_name(engine, f_class, obj_name, env_name=None):
    """
    Function to find objects by name and object class
    :param engine: A Delphix DDP session object
    :type engine: lib.GetSession.GetSession object
    :param f_class: The objects class. I.E. database or timeflow.
    :type f_class: Supported class type by Delphix
    :param obj_name: The name of the object
    :type obj_name: str
    :return: object of f_class type
    """
    if env_name:
        obj_list = f_class.get_all(engine, env_name)
    else:
        obj_list = f_class.get_all(engine)
    for obj in obj_list:
        if obj.name == obj_name:
            return obj
    raise dlpx_exceptions.DlpxObjectNotFound(f"Object {obj_name} not found.")

def find_obj_by_name_v2(engine, f_class, obj_name, *args, **kwargs):
    """
    Function to find objects by name and object class
    :param engine: A Delphix DDP session object
    :type engine: lib.GetSession.GetSession object
    :param f_class: The objects class. I.E. database or timeflow.
    :type f_class: Supported class type by Delphix
    :param obj_name: The name of the object
    :type obj_name: str
    :return: object of f_class type
    """
    obj_name = obj_name.lower()
    obj_list = f_class.get_all(engine, *args, **kwargs)
    for obj in obj_list:
        if str.lower(obj.name) == obj_name:
            return obj
    raise dlpx_exceptions.DlpxObjectNotFound(f"Object {obj_name} not found.")


def find_source_obj_by_containerref(engine, f_class, containerref):
    """
    Function to find objects by name and object class
    :param engine: A Delphix DDP session object
    :type engine: lib.GetSession.GetSession object
    :param f_class: The objects class. I.E. database or timeflow.
    :type f_class: Supported class type by Delphix
    :param obj_name: The name of the object
    :type obj_name: str
    :return: object of f_class type
    """
    obj_list = f_class.get_all(engine)
    for obj in obj_list:
        if obj.container == containerref:
            return obj
    raise dlpx_exceptions.DlpxObjectNotFound(f"Object with container reference {containerref} not found.")


def find_db_by_name_and_group(
        engine, group_name,dbname, exclude_js_container=False
):
    """
    Easy way to quickly find databases by group name and name
    :param engine: A Delphix DDP session object
    :type engine: lib.get_session.GetSession object
    :param group_name: Name of the group for the database
    :type group_name: str
    :param exclude_js_container: If set to true, search self-service
    containers
    :type exclude_js_container: bool
    :return: list of :py:class:`delphixpy.web.vo.Container`
    """
    # First search groups for the name specified and return its reference
    group_ref = find_obj_by_name(engine, group, group_name).reference
    if group_ref:
        databases = database.get_all(
            engine,
            group=group_ref,
            no_js_container_data_source=exclude_js_container,
        )
        for db in databases:
            if db.name == dbname:
                return db
    raise dlpx_exceptions.DlpxObjectNotFound(
        f"Database: {dbname} was not found in group {group_name}"
    )


def find_obj_by_reference(engine, f_class, reference):
    """
    Function to find objects by reference and object class
    :param engine: A Delphix DDP session object
    :type engine: lib.GetSession.GetSession object
    :param f_class: The objects class. I.E. database or timeflow.
    :type f_class: Supported class type by Delphix
    :param obj_name: The refere ce of the object
    :type reference: str
    :return: object of f_class type
    """
    obj_list = f_class.get_all(engine)
    for obj in obj_list:
        if obj.reference == reference:
            return obj
    raise dlpx_exceptions.DlpxObjectNotFound(
        f"Object with reference {reference} not found."
    )

def find_source_by_db_name(engine, obj_name):
    """
    Function to find sources by database name and object class, and return
    object's reference as a string
    :param engine: A Delphix DDP session object
    :type engine: lib.GetSession.GetSession object
    :param obj_name: The name of the database object in Delphix
    :type obj_name: str
    :return: The parent DB object
    """
    for obj in database.get_all(engine):
        if obj.name == obj_name:
            source_obj = source.get_all(engine, database=obj.reference)
            return source_obj[0]
    raise dlpx_exceptions.DlpxObjectNotFound(
        f"{obj_name} was not found on " f"engine {engine.address}.\n"
    )


def find_obj_name(engine, f_class, obj_reference):
    """
    Return the obj name from obj_reference

    :param engine: A Delphix DDP Session object
    :type engine: lib.GetSession.GetSession object
    :param f_class: The objects class. I.E. database or timeflow
    :type f_class: Supported class type by Delphix
    :param obj_reference: The object reference to retrieve the name
    :type obj_reference: str
    :return: str object name
    """
    try:
        obj_name = f_class.get(engine, obj_reference)
        return obj_name.name
    except (
        exceptions.RequestError,
        exceptions.JobError,
        exceptions.HttpError,
    ) as err:
        log.print_exception(err)
        raise dlpx_exceptions.DlpxException(err)


def find_db_repo(engine, install_type, f_environment_ref, f_install_path, install_path_lookup_key=None):
    """
    Function to find database repository objects by environment reference and
    install path, and return the object's reference as a string
    You might use this function to find Oracle and PostGreSQL database repos.
    :param engine: A Delphix DDP session object
    :type engine: lib.GetSession.GetSession object
    :param install_type: Type of install - Oracle, or MSSQL
    :type install_type: str
    :param f_environment_ref: Reference of the environment for the repository
    :type f_install_path: str
    :param f_install_path: Path to the installation directory.
    :type f_install_path: str
    :return: delphixpy.web.vo.SourceRepository object
    """
    for obj in repository.get_all(engine, environment=f_environment_ref):
        if install_type == "OracleInstall":
            if (
                install_type == obj.type
                and obj.installation_home == f_install_path
            ):
                return obj.reference
        elif install_type == "MSSqlInstance":
            if (
                obj.type == install_type
                and obj.instance_name == f_install_path
            ):
                return obj.reference
        elif install_type == "AppDataRepository":
            try:
                if install_path_lookup_key:
                    if install_path_lookup_key in obj.parameters and obj.parameters[install_path_lookup_key] == f_install_path:
                        return obj.reference
                elif obj.type == install_type and obj.parameters['name'] == f_install_path:
                    return obj.reference
            except KeyError:
                if obj.type == install_type and obj.parameters['repositoryName'] == f_install_path:
                    return obj.reference
                else:
                    return None
        else:
            log.print_exception(f'Only OracleInstall, AppDataRepository or MSSqlInstance '
                                f'types are supported.\n')
            raise dlpx_exceptions.DlpxException(
                f"Only OracleInstall, AppDataRepository or MSSqlInstance "
                f"types are supported.\n"
            )


def find_sourceconfig(engine, sourceconfig_name, f_environment_ref):
    """
    Function to find database sourceconfig objects by environment reference,
    sourceconfig name (db name) and return the object
    You might use this function to find Oracle and PostGreSQL database
    sourceconfigs.
    :param engine: A Delphix DDP session object
    :type engine: lib.get_session.GetSession object
    :param sourceconfig_name: Name of source config, usually name of db
    instance (i.e. orcl)
    :type sourceconfig_name: str
    :param f_environment_ref: Reference of the environment for the repository
    :return: Type is determined by sourceonfig. Found in delphixpy.web.objects
    """
    for obj in sourceconfig.get_all(engine, environment=f_environment_ref):
        if obj.name == sourceconfig_name:
            return obj
    raise dlpx_exceptions.DlpxObjectNotFound(
        f"No sourceconfig match found for type {sourceconfig_name}.\n"
    )


def find_all_databases_by_group(
    engine, group_name, exclude_js_container=False
):
    """
    Easy way to quickly find databases by group name
    :param engine: A Delphix DDP session object
    :type engine: lib.get_session.GetSession object
    :param group_name: Name of the group for the database
    :type group_name: str
    :param exclude_js_container: If set to true, search self-service
    containers
    :type exclude_js_container: bool
    :return: list of :py:class:`delphixpy.web.vo.Container`
    """
    # First search groups for the name specified and return its reference
    group_ref = find_obj_by_name(engine, group, group_name).reference
    if group_ref:
        databases = database.get_all(
            engine,
            group=group_ref,
            no_js_container_data_source=exclude_js_container,
        )
        return databases
    raise dlpx_exceptions.DlpxObjectNotFound(
        f"No databases found in " f"group {group_name}.\n"
    )


def find_source_by_database(engine, database_obj):
    """
    The source tells us if the database is enabled/disabled, virtual,
    vdb/dSource, or is a staging database.
    :param engine: Delphix DDP Session object
    :type engine: lib.get_session.GetSession object
    :param database_obj: Delphix database object
    :type database_obj: delphixpy.web.vo.Container
    """
    source_obj = source.get_all(engine, database=database_obj.reference)
    # We'll just do a little sanity check here to ensure we only have a
    # 1:1 result.
    if not source_obj:
        raise dlpx_exceptions.DlpxObjectNotFound(
            f'{engine["hostname"]}: Did not find a source for '
            f"{database_obj.name}."
        )
    elif len(source_obj) > 1:
        raise dlpx_exceptions.DlpxException(
            f'{engine["hostname"]} More than one source returned for '
            f"{database_obj.name}"
        )
    return source_obj


def build_data_source_params(dlpx_obj, obj, data_source):
    """
    Builds the datasource parameters
    :param dlpx_obj: DDP session object
    :type dlpx_obj: lib.GetSession.GetSession object
    :param obj: object type to use when finding db
    :type obj: Type of object to build DS params
    :param data_source: Name of the database to use when building the
    parameters
    :type data_source: str
    """
    ds_params = vo.JSDataSourceCreateParameters()
    ds_params.source = vo.JSDataSource()
    ds_params.source.name = data_source
    try:
        db_obj = find_obj_by_name(dlpx_obj.server_session, obj, data_source)
        ds_params.container = db_obj.reference
        return ds_params
    except exceptions.RequestError as err:
        log.print_exception(f"\nCould not find {data_source}\n{err}")
        raise dlpx_exceptions.DlpxObjectNotFound(
            f"\nCould not find {data_source}\n{err}"
        )


def find_all_objects(engine, f_class):
    """
    Return all objects from a given class
    :param engine: A Delphix engine session object
    :type engine: lib.GetSession.GetSession object
    :param f_class: The objects class. I.E. database or timeflow.
    :return: list
    """
    try:
        return f_class.get_all(engine)
    except (exceptions.JobError, exceptions.HttpError) as err:
        log.print_exception(f"{engine.address} Error encountered in {f_class}: {err}\n")
        raise dlpx_exceptions.DlpxException(
            f"{engine.address} Error encountered in {f_class}: {err}\n"
        )

def find_branch_by_name_and_container_ref(engine,branch_name, container_ref):
    """
    Finds a branch reference by name of the branch and
    referehcen of the container
    :param engine:
    :param container_ref:
    :return:
    """
    try:
        branches = find_all_objects(engine,selfservice.branch)
        if not branches:
            raise Exception
        for branch in branches:
            if branch.data_layout == container_ref and branch.name == branch_name: # noqa
                return branch
        raise Exception
    except Exception as err:
        log.print_exception(f"Could not find branch:{branch_name}"
                            f" in container with ref: {container_ref}")
        raise dlpx_exceptions.DlpxObjectNotFound(f" Could not find branch:{branch_name}"
                                                 f" in container with ref: {container_ref}")


def find_obj_list(obj_lst, obj_name):
    """
    Function to find an object in a list of objects
    :param obj_lst: List containing objects from the get_all() method
    :type obj_lst: list
    :param obj_name: Name of the object to match
    :type obj_name: str
    :return: The named object, otherwise, DlpxObjectNotFound
    """
    for obj in obj_lst:
        if obj_name == obj.name:
            return obj
    raise dlpx_exceptions.DlpxObjectNotFound(f"Did not find {obj_name}\n")


def find_obj_list_by_containername(obj_lst, container_name):
    """
    Function to find an object in a list of objects
    :param obj_lst: List containing objects from the get_all() method
    :type obj_lst: list
    :param obj_name: Name of the object to match
    :type obj_name: str
    :return: The named object, otherwise, DlpxObjectNotFound
    """
    for obj in obj_lst:
        if container_name == obj.container:
            return obj
    raise dlpx_exceptions.DlpxObjectNotFound(
        f"Did not find any object with containername:{container_name}\n")

def find_all_snapshots(engine_session, container_ref, timeflow_ref=None, from_date=None, to_date=None, timestamp=None):
    """
    Retrieves all snapshots for a specific dataset
    with the specified filters applied.
    Allowed filters:
        timeflow_ref: Retrieve snapshots from a specific timeflow.
        from_date: Retrive snapshots after this date.
        to_date: Retrieve snapshots before this date.
    Args:
        engine_session: Session to Delphix Engine
        container_ref: Reference to the dataset.
        timeflow_ref: Reference to timeflow
        from_date: Start date for snapshot.
        to_date: End date for snapshot.
    Returns:
        snapshot_obj: A TimeflowSnapshot object.
    Raises:
        Exception: Generic Exception
    """
    try:
        snapshots = snapshot.get_all(
            engine=engine_session,
            database=container_ref,
            from_date=from_date,
            to_date=to_date
        )
        return snapshots
    except Exception as err:
        log.print_exception(f"There was an error retrieving snapshot for the specified timestamp.{err}")
        raise Exception(f"There was an error retrieving snapshot for the specified timestamp.{err}")

def find_snapshot_by_timestamp(engine_session, container_ref, timestamp):
    """
    Returns the snapshots which can be used to provision
    to this timestamp for the given container.
    Allowed filters:
        timestamp: Timestamp to filter by.
        container_ref: VDB or vFile container object.
    Args:
        engine_session: Session to Delphix Engine
        container_ref: VDB or vFile container object.
        from_date: Start date for snapshot.
        to_date: End date for snapshot.
        timestamp: Timestamp to filter by.
    Returns:
        snapshot_obj: A TimeflowSnapshot object.
    Raises:
        Exception: Generic Exception
    """
    db_tz = None
    utc = UTC
    try:
        # unfortunately, we have to find the timezone of the DB
        # to do this, retrieve snapshots and find the timezone.
        all_snapshots = find_all_snapshots(engine_session,container_ref)
        if all_snapshots is None:
            raise Exception("No snapshots found for the VDB/vFile.")
        db_tz = all_snapshots[0].timezone
        ts_in_utc = convert_timestamp_dbtz_to_utc(timestamp, db_tz, iso_format=True)
        snapshots = snapshot.find_by_timestamp(
            engine=engine_session,
            container=container_ref,
            timestamp=ts_in_utc
        )
        #ts_in_utc = datetime.fromisoformat(ts_in_utc)
        #ts_in_utc= datetime.strptime(ts_in_utc,'%Y-%m-%dT%H:%M:%S.%fZ')
        return (db_tz, snapshots)
    except Exception as err:
        raise Exception(f"There was an error retrieving "
                        f"snapshot for the specified timestamp: {err}")


def find_db_timezone(engine_session, container_ref):
    """
    Returns the timezone for the given container.
    Args:
        engine_session: Session to Delphix Engine
        container_ref: VDB or vFile container object.
    Returns:
        timezone: Timezone string.
    Raises:
        Exception: Generic Exception
    """
    db_tz = None
    try:
        # TODO: Find a better way to do this?
        all_snapshots = find_all_snapshots(engine_session,container_ref)
        if all_snapshots is None:
            raise Exception("No snapshots found for the VDB/vFile.")
        for snapshot_obj in all_snapshots:
            db_tz = snapshot_obj.timezone
            break
        return db_tz
    except Exception as err:
        log.print_exception(f"Unable to find the database timezone:{err}")
        raise Exception(f"Unable to find the database timezone:{err}")
