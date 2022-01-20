
def test_version():
    import gammalearn
    # when running unit tests, gammalearn is supposed to have been installed correctly
    # then the version must be accessible and different from  0.0.0
    assert gammalearn.__version__ != '0.0.0'

