# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
A module for creating and submitting manual submissions to autoreduction
"""
from typing import Iterable, List, Optional, Tuple, Union
import logging
import traceback

import fire
import h5py

from autoreduce_utils.clients.connection_exception import ConnectionException
from autoreduce_utils.clients.icat_client import ICATClient
from autoreduce_utils.clients.queue_client import QueueClient
from autoreduce_utils.clients.tools.isisicat_prefix_mapping import get_icat_instrument_prefix
from autoreduce_utils.message.message import Message

from autoreduce_scripts.manual_operations.rb_categories import RBCategory
from autoreduce_scripts.manual_operations import setup_django

setup_django()

# pylint:disable=wrong-import-order,wrong-import-position,no-member,too-many-arguments,too-many-return-statements

from autoreduce_db.reduction_viewer.models import ReductionRun

logger = logging.getLogger(__file__)


def submit_run(
    active_mq_client,
    rb_number: Union[str, List[str]],
    instrument: str,
    data_file_location: Union[str, List[str]],
    run_number: Union[int, Iterable[int]],
    run_title: Union[str, List[str]],
    software: Optional[dict] = None,
    reduction_script: str = None,
    reduction_arguments: dict = None,
    user_id=-1,
    description="",
) -> dict:
    """
    Submit a new run for autoreduction

    Args:
        active_mq_client: The client for access to ActiveMQ
        rb_number: desired experiment rb number
        instrument: name of the instrument
        data_file_location: location of the data file
        run_number: run number fo the experiment

    Returns:
        The dict representation of the message that was submitted to ActiveMQ
    """
    if active_mq_client is None:
        raise RuntimeError("ActiveMQ not connected, cannot submit runs")

    message = Message(rb_number=rb_number,
                      instrument=instrument,
                      data=data_file_location,
                      run_number=run_number,
                      facility="ISIS",
                      started_by=user_id,
                      reduction_script=reduction_script,
                      reduction_arguments=reduction_arguments,
                      description=description,
                      run_title=run_title,
                      software=software)
    active_mq_client.send('/queue/DataReady', message, priority=1)
    logger.info("Submitted run: %s", message.serialize(indent=1))
    return message.to_dict()


def get_run_data_from_database(instrument: str, run_number: int) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Retrieves a run's data-file location and rb_number from the auto-reduction database
    Args:
        database_client: Client to access auto-reduction database
        instrument: The name of the instrument associated with the run
        run_number: The run number of the data to be retrieved
    Returns:
         The data file location and rb_number, or None if this information is not in the database
    """

    # Find the latest version of a reduction run record to read information from it.
    # Does NOT include batch runs, instead looks at individual runs
    reduction_run_record = ReductionRun.objects.filter(instrument__name=instrument,
                                                       run_numbers__run_number=run_number,
                                                       batch_run=False).order_by('run_version').first()

    if not reduction_run_record:
        return None, None, None

    data_location = reduction_run_record.data_location.first().file_path
    experiment_number = str(reduction_run_record.experiment.reference_number)
    run_title = reduction_run_record.run_title

    return data_location, experiment_number, run_title


def icat_datafile_query(icat_client, file_name):
    """
    Search for file name in icat and return it if it exist.

    Args:
        icat_client: Client to access the ICAT service
        file_name: file name to search for in icat
    Returns:
        ICAT datafile entry if found
    """
    if icat_client is None:
        raise RuntimeError("ICAT not connected")

    return icat_client.execute_query("SELECT df FROM Datafile df WHERE df.name = '" + file_name +
                                     "' INCLUDE df.dataset AS ds, ds.investigation")


def get_run_data_from_icat(instrument, run_number, file_ext) -> Tuple[str, str]:
    """
    Retrieves a run's data-file location and rb_number from ICAT.
    Attempts first with the default file name, then with prepended zeroes.

    Args:
        icat_client: Client to access the ICAT service
        instrument: The name of instrument
        run_number: The run number to be processed
        file_ext: The expected file extension

    Returns:
        The data file location, rb_number (experiment reference) and run_title
    """
    icat_client = login_icat()

    # look for file-name assuming file-name uses prefix instrument name
    icat_instrument_prefix = get_icat_instrument_prefix(instrument)
    file_name = f"{icat_instrument_prefix}{str(run_number).zfill(5)}.{file_ext}"
    datafile = icat_datafile_query(icat_client, file_name)

    if not datafile:
        logger.info("Cannot find datafile '%s' in ICAT. Will try with zeros in front of run number.", file_name)
        file_name = f"{icat_instrument_prefix}{str(run_number).zfill(8)}.{file_ext}"
        datafile = icat_datafile_query(icat_client, file_name)

    # look for file-name assuming file-name uses full instrument name
    if not datafile:
        logger.info("Cannot find datafile '%s' in ICAT. Will try using full instrument name.", file_name)
        file_name = f"{instrument}{str(run_number).zfill(5)}.{file_ext}"
        datafile = icat_datafile_query(icat_client, file_name)

    if not datafile:
        logger.info("Cannot find datafile '%s' in ICAT. Will try with zeros in front of run number.", file_name)
        file_name = f"{instrument}{str(run_number).zfill(8)}.{file_ext}"
        datafile = icat_datafile_query(icat_client, file_name)

    if not datafile:
        raise RuntimeError(f"Cannot find datafile '{file_name}' in ICAT.")
    return datafile[0].location, datafile[0].dataset.investigation.name


def overwrite_icat_calibration_placeholder(location: str, value: Union[str, int], key: str) -> str:
    """
    Checks if the value provided has been overwritten by ICAT with calibration run placeholder text.

    Returns:
        The real value read from the NXS data file logs directly.
    """
    value = str(value)

    if "CAL" in value:
        value = read_from_datafile(location, key)

    return value


def get_run_data(instrument: str, run_number: Union[str, int], file_ext: str) -> Tuple[str, str, str]:
    """
    Retrieves a run's data-file location and rb_number from the auto-reduction database,
    or ICAT (if it is not in the database)

    Args:
        instrument: The name of instrument
        run_number: The run number to be processed
        file_ext: The expected file extension

    Returns:
        The data file location and rb_number
    """
    try:
        parsed_run_number = int(run_number)
    except ValueError:
        logger.error("Cannot cast run_number as an integer. Run number given: '%s'. Exiting...", run_number)
        raise

    data_location, experiment_number, run_title = get_run_data_from_database(instrument, parsed_run_number)
    if data_location is not None and experiment_number is not None and run_title is not None:
        return data_location, experiment_number, run_title
    logger.info("Cannot find datafile for run_number %s in Auto-reduction database. "
                "Will try ICAT...", parsed_run_number)

    location, rb_num = get_run_data_from_icat(instrument, parsed_run_number, file_ext)

    # ICAT seems to do some replacements for calibration runs, overwriting the real RB number & the title
    rb_num = overwrite_icat_calibration_placeholder(location, rb_num, 'experiment_identifier')
    run_title = read_from_datafile(location, 'title')
    return location, rb_num, run_title


def login_icat() -> ICATClient:
    """
    Log into the ICATClient

    Returns:
        The client connected, or None if failed
    """
    print("Logging into ICAT")
    icat_client = ICATClient()
    try:
        icat_client.connect()
    except ConnectionException as exc:
        print("Couldn't connect to ICAT. Continuing without ICAT connection.")
        raise RuntimeError("Unable to proceed. Unable to connect to ICAT.") from exc
    return icat_client


def login_queue() -> QueueClient:
    """
    Log into the QueueClient

    Returns:
        The client connected, or raise exception
    """
    print("Logging into ActiveMQ")
    activemq_client = QueueClient()
    try:
        activemq_client.connect()
    except (ConnectionException, ValueError) as exp:
        raise RuntimeError(
            "Cannot connect to ActiveMQ with provided credentials in credentials.ini\n"
            "Check that the ActiveMQ service is running, and the username, password and host are correct.") from exp
    return activemq_client


def windows_to_linux_path(path) -> str:
    """ Convert windows path to linux path.

    Args:
        path: The path that will be converted

    Returns:
        Linux formatted file path
    """
    # '\\isis\inst$\' maps to '/isis/'
    path = path.replace('\\\\isis\\inst$\\', '/isis/')
    path = path.replace('\\', '/')
    return path


def read_from_datafile(location: str, key: str) -> str:
    """
    Reads the RB number from the location of the datafile

    Args:
        location: The location of the datafile

    Returns:
        The RB number read from the datafile
    """

    location = windows_to_linux_path(location)
    try:
        nxs_file = h5py.File(location, mode="r")
    except OSError as err:
        raise RuntimeError(f"Cannot open file '{location}'") from err

    for (_, entry) in nxs_file.items():
        try:
            return str(entry.get(key)[:][0].decode("utf-8"))
        except Exception as err:
            raise RuntimeError("Could not read RB number from datafile") from err
    raise RuntimeError(f"Datafile at {location} does not have any items that can be iterated")


def categorize_rb_number(rb_num: str):
    """
    Map RB number to a category. If an ICAT calibration RB number is provided,
    the datafile will be checked to find out the real experiment number.

    This is because ICAT will overwrite the real RB number for calibration runs!
    """
    if len(rb_num) != 7:
        return RBCategory.UNCATEGORIZED

    if rb_num[2] == "0":
        return RBCategory.DIRECT_ACCESS
    elif rb_num[2] in ["1", "2"]:
        return RBCategory.RAPID_ACCESS
    elif rb_num[2] == "3" and rb_num[3] == "0":
        return RBCategory.COMMISSIONING
    elif rb_num[2] == "3" and rb_num[3] == "5":
        return RBCategory.CALIBRATION
    elif rb_num[2] == "5":
        return RBCategory.INDUSTRIAL_ACCESS
    elif rb_num[2] == "6":
        return RBCategory.INTERNATIONAL_PARTNERS
    elif rb_num[2] == "9":
        return RBCategory.XPESS_ACCESS
    else:
        return RBCategory.UNCATEGORIZED


def main(instrument: str,
         runs: Union[int, Iterable[int]],
         software: Optional[dict] = None,
         reduction_script: Optional[str] = None,
         reduction_arguments: Optional[dict] = None,
         user_id=-1,
         description="") -> list:
    """
    Manually submit an instrument run from reduction.
    All run number between `first_run` and `last_run` are submitted.

    Args:
        instrument: The name of the instrument to submit a run for
        runs: The run or runs to be submitted. If a list then all the run numbers in it will be submitted
        software: The software to be used for reduction (e.g. {'name': 'ISIS', 'version': '1.0'})
        reduction_script: The reduction script to be used. If not provided,
                          the default reduction script for the instrument will be used.
                          Currently unused as the queue processor will ignore the value
                          and always use the current reduce.py.
                          Issue tracking this https://autoreduce.atlassian.net/browse/AR-1056
        reduction_arguments: The arguments to be passed to the reduction script,
                                if None the reduce_vars.py file will be loaded
        user_id: The user ID that submitted the request. Using this script directly
                 and the run detection use -1, which is mapped to "Autoreduction service"
        description: A custom description of the run, if provided by the user

    Returns:
        A list of run numbers that were submitted.
    """

    instrument = instrument.upper()

    activemq_client = login_queue()

    submitted_runs = []

    if not isinstance(runs, Iterable):
        runs = [runs]

    for run_number in runs:
        location, rb_num, run_title = get_run_data(instrument, run_number, "nxs")
        if not location and not rb_num:
            logger.error("Unable to find RB number and location for %s%s", instrument, run_number)
            continue
        try:
            category = categorize_rb_number(rb_num)
            logger.info("Run is in category %s", category)
        except RuntimeError:
            logger.warning("Could not categorize the run due to an invalid RB number. It will be not be submitted.\n%s",
                           traceback.format_exc())
            continue

        submitted_runs.append(
            submit_run(activemq_client,
                       rb_num,
                       instrument,
                       location,
                       run_number,
                       run_title=run_title,
                       software=software,
                       reduction_script=reduction_script,
                       reduction_arguments=reduction_arguments,
                       user_id=user_id,
                       description=description))

    return submitted_runs


def fire_entrypoint():
    """
    Entrypoint into the Fire CLI interface. Used via setup.py console_scripts
    """
    fire.Fire(main)  # pragma: no cover


if __name__ == "__main__":
    fire.Fire(main)  # pragma: no cover
