import logging
from typing import Iterable, Optional

import fire

from autoreduce_scripts.manual_operations import setup_django

setup_django()

# pylint:disable=wrong-import-position
from autoreduce_scripts.manual_operations.manual_submission import get_run_data, login_queue, submit_run


def all_equal(iterator):
    """Tests that all elements in a list are equal"""
    iterator = iter(iterator)
    try:
        first = next(iterator)
    except StopIteration:
        return True
    return all(first == x for x in iterator)


# pylint: disable=too-many-locals
def main(instrument,
         runs: Iterable[int],
         software: Optional[dict] = None,
         reduction_script: Optional[str] = None,
         reduction_arguments: Optional[dict] = None,
         user_id: int = -1,
         description: str = ""):
    """Submits the runs for this instrument as a single reduction"""

    logger = logging.getLogger(__file__)
    logger.info("Submitting runs %s for instrument %s", runs, instrument)
    instrument = instrument.upper()

    activemq_client = login_queue()
    locations, rb_numbers, titles = [], [], []
    for run in runs:
        location, rb_num, run_title = get_run_data(instrument, run, "nxs")
        locations.append(location)
        rb_numbers.append(rb_num)
        titles.append(run_title)
    if not all_equal(rb_numbers):
        raise RuntimeError("Submitted runs have mismatching RB numbers")
    return submit_run(activemq_client,
                      rb_numbers[0],
                      instrument,
                      locations,
                      runs,
                      run_title=titles,
                      software=software,
                      reduction_script=reduction_script,
                      reduction_arguments=reduction_arguments,
                      user_id=user_id,
                      description=description)


def fire_entrypoint():
    """
    Entrypoint into the Fire CLI interface. Used via setup.py console_scripts
    """
    fire.Fire(main)  # pragma: no cover


if __name__ == "__main__":
    fire.Fire(main)  # pragma: no cover
