from pollination_handlers.inputs.runperiod import run_period_to_str

from ladybug.analysisperiod import AnalysisPeriod
import pytest


def test_north_vector_to_angle():
    r_per_1 = AnalysisPeriod(3, 21, 0, 6, 21, 23)
    r_per_2 = AnalysisPeriod(6, 21, 0, 3, 21, 23)

    assert isinstance(run_period_to_str(r_per_1), str)
    assert isinstance(run_period_to_str(r_per_2), str)
