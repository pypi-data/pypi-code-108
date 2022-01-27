from pyquanttrade.engine.commands import backtest, backtest_and_visualise
from tests.policy_battery import test_policy_1
from tests.policy_battery import test_policy_2

def test_backtest():
    backtest(test_policy_2,"TSLA", "2012-01-01", "2021-01-01")

def test_backtest_and_visualise():
    backtest_and_visualise(test_policy_2,"TSLA", "2012-01-01", "2021-01-01")
