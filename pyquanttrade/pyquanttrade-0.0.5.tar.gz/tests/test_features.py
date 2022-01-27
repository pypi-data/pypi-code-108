from pyquanttrade.features import functions, indicators
from pyquanttrade.market import marketData

# Test two functions to check proper execution
def test_functions():
    data = marketData.get_data("AAPL", "2010-01-01", "2021-01-01")
    test_func_data_1 = functions.special_k()(data)
    test_func_data_2 = functions.triangular_weighting_ma()(data)
    assert (len(test_func_data_1) != 0) & (test_func_data_1 is not None)
    assert (len(test_func_data_2) != 0) & (test_func_data_2 is not None)

# Test two indicators to check proper execution
def test_indicators():
    data = marketData.get_data("AAPL", "2010-01-01", "2021-01-01")
    test_func_1 = functions.special_k()
    test_func_2 = functions.triangular_weighting_ma()
    cross_of_values_data = indicators.cross_of_values(test_func_1,test_func_2)('2010-12-10',None,None,data)
    greater_than_data = indicators.greater_than(test_func_1,test_func_2)('2010-12-10',None,None,data)
    assert  cross_of_values_data is not None
    assert greater_than_data is not None
