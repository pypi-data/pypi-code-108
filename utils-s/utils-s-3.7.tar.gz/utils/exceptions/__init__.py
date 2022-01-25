# global unspecific exceptions
class utilityErrors(Exception):
    pass


class pathError(utilityErrors):
    pass


class Depreciated(utilityErrors):
    pass


class DepreciatedFunction(Exception):
    def __init__(self, source, function_name):
        errmsg = """The function .{}() from {} is deprecated""".format(function_name, source)
        raise Depreciated(errmsg)
