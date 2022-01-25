# Copyright (c) 8080 Labs GmbH.
# Distributed under the terms of our End-User License Agreement (see bamboolib.com/eula
# for more information).


def get_user_symbols():
    """
    Returns the dictionary of the user's symbols.

    ATTENTION: this function does not work when the code is called from a thread!
    """
    import inspect
    from bamboolib import _environment as env

    if env.TESTING_MODE:
        # When we are running the bamboolib tests, we need to get the symbols from another frame
        for index, item in enumerate(inspect.stack()):
            try:
                name = item[0].f_globals["__name__"]
                if name.startswith("test_"):
                    return item[0].f_globals
            except:  # __name__ attribute does not exist
                pass
    else:
        # When bamboolib is run by the user, we get the symbols from the __main__ script
        for index, item in enumerate(inspect.stack()):
            try:
                name = item[0].f_globals["__name__"]
                if name == "__main__":
                    return item[0].f_globals
            except:  # __name__ attribute does not exist
                pass
    return {}
