# detect lxml availability

import typing

from momotor.bundles.exception import LxmlMissingError

__all__ = ['use_lxml', 'detect_lxml']


has_lxml = None


def detect_lxml() -> bool:
    """ Helper to detect :py:mod:`lxml` package availability

    :return: `True` if :py:mod:`lxml` is installed
    """
    global has_lxml

    if has_lxml is None:
        try:
            import lxml  # noqa
            has_lxml = True
        except ImportError:
            has_lxml = False
        else:
            del lxml

    return has_lxml


def use_lxml(use: typing.Optional[bool]) -> bool:
    """ Helper to interpret `use_lxml` argument

    :param: Provided `use_lxml` argument
    :return: `True` if :py:mod:`lxml` should be used
    """
    if use is None:
        return detect_lxml()

    elif use and not has_lxml:
        raise LxmlMissingError("To use lxml, install the momotor-bundles package "
                               "with the lxml option: momotor-bundles[lxml]")
    return use
