# pytest configurations file


def pytest_sessionstart(session):
    print("START BAMBOOLIB TESTS")
    from bamboolib import _environment as env

    # True is default
    env.TESTING_MODE = True
    env.DEACTIVATE_ASYNC_CALLS = True
    env.TEST_BIVARIATE_PLOTS = True
