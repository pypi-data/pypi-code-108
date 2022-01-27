from pathlib import Path
from unittest.mock import patch
import shutil

from django.contrib.staticfiles.testing import LiveServerTestCase
from django.utils import timezone

from autoreduce_scripts.checks import setup_django  # pylint:disable=wrong-import-order,ungrouped-imports
from autoreduce_db.reduction_viewer.models import Instrument, ReductionRun
from autoreduce_scripts.checks.daily.time_since_last_run import BASE_INSTRUMENT_LASTRUNS_TXT_DIR, main

# pylint:disable=no-member,no-self-use

setup_django()


class TimeSinceLastRunTest(LiveServerTestCase):
    """
    Test the behaviour when none of the instruments runs match the number in lastruns.txt
    """
    fixtures = ["status_fixture", "multiple_instruments_and_runs"]

    def setUp(self) -> None:
        self.instruments = Instrument.objects.all()
        for instrument in self.instruments:
            log_path = Path(BASE_INSTRUMENT_LASTRUNS_TXT_DIR.format(instrument))
            log_path.mkdir(parents=True, exist_ok=True)
            last_runs_txt = log_path / "lastrun.txt"
            last_runs_txt.write_text(f"{instrument} 44444 0", encoding="utf-8")

    def tearDown(self) -> None:
        for instrument in self.instruments:
            log_path = Path(BASE_INSTRUMENT_LASTRUNS_TXT_DIR.format(instrument))
            shutil.rmtree(log_path)

    @patch("autoreduce_scripts.checks.daily.time_since_last_run.logging")
    def test_with_multiple_instruments(self, mock_logging):
        """
        Test when there are multiple instruments that haven't had run in a day.
        """
        main()
        assert mock_logging.getLogger.return_value.warning.call_count == 2

    @patch("autoreduce_scripts.checks.daily.time_since_last_run.logging")
    def test_only_one_doesnt_have_runs(self, mock_logging):
        """
        Test when one instrument hasn't had runs, but one has.
        Only one of them should cause a log message.
        """
        rr2 = ReductionRun.objects.get(pk=2)
        rr2.created = timezone.now()
        rr2.save()
        main()
        mock_logging.getLogger.return_value.warning.assert_called_once()

    @patch("autoreduce_scripts.checks.daily.time_since_last_run.logging")
    def test_all_have_runs(self, mock_logging):
        """
        Test when one instrument hasn't had runs, but one has.
        Only one of them should cause a log message.
        """
        for redrun in ReductionRun.objects.all():
            redrun.created = timezone.now()
            redrun.save()
        main()
        mock_logging.getLogger.return_value.warning.assert_not_called()

    @patch("autoreduce_scripts.checks.daily.time_since_last_run.logging")
    def test_paused_instruments_not_reported(self, mock_logging):
        """
        Test when one instrument hasn't had runs, but one has.
        Only one of them should cause a log message.
        """
        last_instr = Instrument.objects.last()
        last_instr.is_paused = True
        last_instr.save()
        main()
        mock_logging.getLogger.return_value.info.assert_called_once()
        mock_logging.getLogger.return_value.warning.assert_called_once()

    @patch("autoreduce_scripts.checks.daily.time_since_last_run.logging")
    def test_instrument_without_runs(self, mock_logging):
        """
        Test when one instrument hasn't had runs, but one has.
        Only one of them should cause a log message.
        """
        last_instr = Instrument.objects.last()
        last_instr.reduction_runs.all().delete()
        main()
        mock_logging.getLogger.return_value.warning.assert_called_once()
