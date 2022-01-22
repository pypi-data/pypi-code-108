def multiprint(stuffToPrint, _=None, *args, **kwargs):
    """
    Accepts a dictionary. With key/value pairs text/function.
    For example, you might pass {"Welcome to ": cprint.info, "Palc": cprint.ok, "!" + MANYSPACE: cprint.info}
    which will run cprint.info("Welcome to ");cprint.ok("Palc");cprint.info("!" + MANYSPACE)
    Setting _ to a function will run whateverFunctionYouPassed(_(item), *args, **kwargs) instead of just whateverFunctionYouPassed(item, *args, **kwargs).
    The **kwargs and *args are given to EVERY function, *args first. Useful as an "end=True" or similar.
    Note: To use *args and **kwargs, you MUST write the function like so: multiprint(theDictionary, _=None, *args, **kwargs) instead of multiprint(theDictionary, *args, **kwargs).
    If using print or cprint, it is **highly recommended** to add flush=True to the end of the function call, because otherwise you may run into issues with the print() cache.
    """
    if _ is None:
        def _(string):
            return string
    for item in stuffToPrint:
        stuffToPrint[item](_(item), *args, **kwargs)

