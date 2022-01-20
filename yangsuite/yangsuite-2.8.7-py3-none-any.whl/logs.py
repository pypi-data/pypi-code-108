# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.

import logging


def get_logger(name=''):
    """Get a logger with the given name under the ``yangsuite`` namespace.

    >>> get_logger('ysdevices.devprofile').name
    'yangsuite.ysdevices.devprofile'
    >>> get_logger('ysyangtree').name
    'yangsuite.ysyangtree'
    >>> get_logger('foo.bar').name
    'yangsuite.foo.bar'
    >>> get_logger().name
    'yangsuite'
    >>> get_logger('').name
    'yangsuite'

    If the name is already under ``yangsuite``, will not add it again:

    >>> get_logger('yangsuite').name
    'yangsuite'
    >>> get_logger('yangsuite.logs').name
    'yangsuite.logs'
    """
    if name.startswith('yangsuite'):
        pass
    elif name:
        name = 'yangsuite.' + name
    else:
        name = 'yangsuite'
    return logging.getLogger(name)


if __name__ == "__main__":  # pragma: no cover
    import doctest
    doctest.testmod()
