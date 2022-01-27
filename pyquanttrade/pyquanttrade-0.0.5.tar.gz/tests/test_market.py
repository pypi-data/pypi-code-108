from pyquanttrade.market import marketData

def test_get_data():
    data = marketData.get_data("AAPL", "2010-01-01", "2022-01-01")
    assert len(data) != 0

def test_get_data_lt():
    data = marketData.get_data_lt("AAPL", "2010-01-01")
    assert len(data) != 0
   

def test_get_data_and_visualize():
    marketData.get_data_and_visualize("AAPL", "2010-01-01", "2021-01-01")