def load_dialect_module(dialect_name):
    from importlib import import_module
    if dialect_name != 'standard':
        dialect = import_module('camtono.dialects.{}'.format(dialect_name))
    else:
        dialect = import_module('camtono.parser.{}'.format(dialect_name))
    return dialect


def list_dialects():
    """

    :return:
    """
    import pkgutil
    try:
        import camtono.dialects
    except ModuleNotFoundError:
        pass
    else:
        for finder, modname, ispkg in pkgutil.iter_modules(camtono.dialects.__path__):
            yield modname
    finally:
        yield "standard"
