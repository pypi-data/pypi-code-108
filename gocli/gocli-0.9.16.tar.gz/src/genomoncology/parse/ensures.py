import types


def ensure_collection(x):
    """ Ensures the parameter provided is an iterable """

    if x is None:
        x = []

    elif isinstance(x, types.GeneratorType):
        x = list(x)

    elif not isinstance(x, (list, tuple, set)):
        x = [x]

    return x


# reference: http://stackoverflow.com/a/12472564
def flatten(x):

    if isinstance(x, (tuple, types.GeneratorType)):
        x = list(x)

    if x == []:
        return x

    if isinstance(x[0], (tuple, list, types.GeneratorType)):
        return flatten(x[0]) + flatten(x[1:])

    return x[:1] + flatten(x[1:])
