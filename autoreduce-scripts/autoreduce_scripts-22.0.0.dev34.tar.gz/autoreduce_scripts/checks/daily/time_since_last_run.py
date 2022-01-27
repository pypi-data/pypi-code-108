"""
Checks the time since the last run for each instrument.

If over 1 day it logs a warning.
"""
import logging
import os
from datetime import timedelta
from pathlib import Path

from autoreduce_utils.settings import ARCHIVE_ROOT

from django.utils import timezone

from autoreduce_scripts.checks import setup_django  # setup_django first or importing the model fails

setup_django()

# pylint:disable=wrong-import-position,wrong-import-order
from autoreduce_db.reduction_viewer.models import Instrument

# pylint:disable=no-member

BASE_INSTRUMENT_LASTRUNS_TXT_DIR = os.path.join(ARCHIVE_ROOT, "NDX{}", "Instrument", "logs")


def main():
    """
    Run through all instruments and check how long it's been since their last run.

    If the instrument is paused we don't log anything.

    The log file should then be sent to Kibana where we have alerts.
    """
    setup_django()
    logger = logging.getLogger(os.path.basename(__file__))
    instruments = Instrument.objects.all()

    for instrument in instruments:
        if instrument.is_paused:  # skip paused instruments, we are not processing runs for them
            logger.info("Instrument %s is paused", instrument)
            continue
        last_runs_txt_file = Path(BASE_INSTRUMENT_LASTRUNS_TXT_DIR.format(instrument), "lastrun.txt")
        last_runs_txt = last_runs_txt_file.read_text(encoding="utf-8")

        last_run = instrument.reduction_runs.last()
        if last_run and timezone.now() - last_run.created > timedelta(1):
            # don't use batch runs to check when the last run was
            if last_run.batch_run:
                continue
            if str(last_run.run_number) not in last_runs_txt:
                logger.warning("Instrument %s has not had runs in over 1 day", instrument)
            else:
                logger.info("Last run for instrument %s matches lastrun.txt", instrument)
        else:
            logger.info("All runs OK for instrument %s", instrument)


if __name__ == "__main__":
    main()
