from pathlib import Path
from unittest.mock import patch
import shutil
from django.contrib.staticfiles.testing import LiveServerTestCase

from autoreduce_scripts.checks import setup_django  # pylint:disable=wrong-import-order,ungrouped-imports
from autoreduce_db.reduction_viewer.models import Instrument
from autoreduce_scripts.checks.daily.time_since_last_run import BASE_INSTRUMENT_LASTRUNS_TXT_DIR, main

# pylint:disable=no-member,no-self-use

setup_django()


class TimeSinceLastRunMatchingLastrunsTest(LiveServerTestCase):
    """
    Test the behaviour when the last runs matches the lastruns.txt contents
    """
    fixtures = ["status_fixture", "multiple_instruments_and_runs"]

    def setUp(self) -> None:
        self.instruments = Instrument.objects.all()
        for instrument in self.instruments:
            log_path = Path(BASE_INSTRUMENT_LASTRUNS_TXT_DIR.format(instrument))
            log_path.mkdir(parents=True, exist_ok=True)
            last_runs_txt = log_path / "lastrun.txt"
            last_runs_txt.write_text(f"{instrument} {instrument.reduction_runs.last().run_number} 0", encoding="utf-8")

    def tearDown(self) -> None:
        for instrument in self.instruments:
            log_path = Path(BASE_INSTRUMENT_LASTRUNS_TXT_DIR.format(instrument))
            shutil.rmtree(log_path)

    @patch("autoreduce_scripts.checks.daily.time_since_last_run.logging")
    def test_with_multiple_instruments(self, mock_logging):
        """
        Test when there are multiple instruments that haven't had run in a day, but they are also
        the last runs recorded in lastruns.txt - we are not expecting anything to be logged, as the
        beamline hasn't had any new runs that need processing
        """
        main()
        mock_logging.getLogger.return_value.warning.assert_not_called()
        assert mock_logging.getLogger.return_value.info.call_count == 2
