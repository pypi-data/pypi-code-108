import logging

from .read import read_ipynb
from .utils import GREEN, LIGHTPURPLE, NC, RED


def assert_no_errors(errors):
    if not (errors == [] or errors is None):
        raise AssertionError
    # assert errors == [] or errors is None


def test_ipynb(notebook_filename, debug):

    # First read the ipynb notebook into a python dictionary
    nb, errors = read_ipynb(notebook_filename, True, debug)

    print("")
    print(LIGHTPURPLE, "*".center(80, "*"), NC)
    print(LIGHTPURPLE, "Testing output notebook:\n", NC, notebook_filename)
    logging.info("Testing output notebook" + str(notebook_filename))
    test_result = False

    # Check for errors and catch them
    try:
        test_result = assert_no_errors(errors)
        test_result = True
    except AssertionError as e:
        print(RED, type(e), "\n", e)
        errors.append("ASSERTION ERROR")
        logging.error(e)
        print(NC)
    except BaseException as e:
        print(RED, type(e), "\n", e)
        errors.append("UNKNOWN ERROR")
        logging.error(e)
        print(NC)

    # Print final result
    COLOR = GREEN if test_result else RED
    print(COLOR, "-".center(80, "-"))
    print(COLOR, " test result: " + str(test_result))
    print(COLOR, "-".center(80, "-"), NC)

    # Log result
    logging.info("test result: " + str(test_result))
    logging.info("Done testing " + str(notebook_filename))

    for error_message in errors:
        print(RED, error_message, NC)
    print(LIGHTPURPLE, "Done testing")
    print(LIGHTPURPLE, "*".center(80, "*"), NC)
    print("")

    return test_result
